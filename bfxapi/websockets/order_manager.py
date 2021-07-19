"""
Module used to house all of the functions/classes used to handle orders
"""

import time
import asyncio

from ..utils.custom_logger import CustomLogger
from ..models import Order
from ..utils.auth import calculate_order_flags, gen_unique_cid


class OrderManager:
    """
    Handles all of the functionality for opening, updating and closing order.
    Also contains state such as all of your open orders and orders that have
    closed.
    """

    def __init__(self, bfxapi, logLevel='INFO'):
        self.bfxapi = bfxapi
        self.pending_orders = {}
        self.closed_orders = {}
        self.open_orders = {}

        self.pending_order_close_callbacks = {}
        self.pending_order_confirm_callbacks = {}
        self.pending_update_confirm_callbacks = {}
        self.pending_cancel_confirm_callbacks = {}
        self.logger = CustomLogger('BfxOrderManager', logLevel=logLevel)

    def get_open_orders(self):
        return list(self.open_orders.values())

    def get_closed_orders(self):
        return list(self.closed_orders.values())

    def get_pending_orders(self):
        return list(self.pending_orders.values())

    async def confirm_order_closed(self, raw_ws_data):
        order = Order.from_raw_order(raw_ws_data[2])
        order.set_open_state(False)
        if order.id in self.open_orders:
            del self.open_orders[order.id]
        if order.cid in self.pending_orders:
            del self.pending_orders[order.cid]
        self.closed_orders[order.id] = order
        if not order.is_confirmed():
            order.set_confirmed()
            self.bfxapi._emit('order_confirmed', order)
        await self._execute_callback(order, self.pending_order_confirm_callbacks)
        await self._execute_callback(order, self.pending_cancel_confirm_callbacks)
        await self._execute_callback(order, self.pending_update_confirm_callbacks)
        await self._execute_callback(order, self.pending_order_close_callbacks)
        self.logger.info("Order closed: {} {}".format(
            order.symbol, order.status))
        self.bfxapi._emit('order_closed', order)

    async def build_from_order_snapshot(self, raw_ws_data):
        """
        Rebuild the user orderbook based on an incoming snapshot
        """
        osData = raw_ws_data[2]
        self.open_orders = {}
        for raw_order in osData:
            order = Order.from_raw_order(raw_order)
            order.set_open_state(True)
            self.open_orders[order.id] = order
        self.bfxapi._emit('order_snapshot', self.get_open_orders())

    async def confirm_order_update(self, raw_ws_data):
        order = Order.from_raw_order(raw_ws_data[2])
        order.set_open_state(True)
        self.open_orders[order.id] = order
        await self._execute_callback(order, self.pending_update_confirm_callbacks)
        self.logger.info("Order update: {}".format(order))
        self.bfxapi._emit('order_update', order)

    async def confirm_order_new(self, raw_ws_data):
        order = Order.from_raw_order(raw_ws_data[2])
        order.set_open_state(True)
        if order.cid in self.pending_orders:
            del self.pending_orders[order.cid]
        self.open_orders[order.id] = order
        order.set_confirmed()
        self.bfxapi._emit('order_confirmed', order)
        await self._execute_callback(order, self.pending_order_confirm_callbacks)
        self.logger.info("Order new: {}".format(order))
        self.bfxapi._emit('order_new', order)

    async def confirm_order_error(self, raw_ws_data):
        cid = raw_ws_data[2][4][2]
        if cid in self.pending_orders:
            del self.pending_orders[cid]
        self.logger.info("Deleted Order CID {} from pending orders".format(cid))

    async def submit_order(self, symbol, price, amount, market_type=Order.Type.LIMIT,
                           hidden=False, price_trailing=None, price_aux_limit=None,
                           oco_stop_price=None, close=False, reduce_only=False,
                           post_only=False, oco=False, aff_code=None, time_in_force=None,
                           leverage=None, onConfirm=None, onClose=None, gid=None, *args, **kwargs):
        """
        Submit a new order

        @param gid: assign the order to a group identifier
        @param symbol: the name of the symbol i.e 'tBTCUSD
        @param price: the price you want to buy/sell at (must be positive)
        @param amount: order size: how much you want to buy/sell,
          a negative amount indicates a sell order and positive a buy order
        @param market_type	Order.Type: please see Order.Type enum
          amount	decimal string	Positive for buy, Negative for sell
        @param hidden: if True, order should be hidden from orderbooks
        @param price_trailing:	decimal trailing price
        @param price_aux_limit:	decimal	auxiliary Limit price (only for STOP LIMIT)
        @param oco_stop_price: set the oco stop price (requires oco = True)
        @param close: if True, close position if position present
        @param reduce_only: if True, ensures that the executed order does not flip the opened position
        @param post_only: if True, ensures the limit order will be added to the order book and not
          match with a pre-existing order
        @param oco: cancels other order option allows you to place a pair of orders stipulating
          that if one order is executed fully or partially, then the other is automatically canceled
        @param aff_code: bitfinex affiliate code
        @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
        @param leverage: the amount of leverage to apply to the order as an integer
        @param onConfirm: function called when the bitfinex websocket receives signal that the order
          was confirmed
        @param onClose: function called when the bitfinex websocket receives signal that the order
          was closed due to being filled or cancelled
        """
        cid = self._gen_unique_cid()
        # create base payload with required data
        payload = {
            "cid": cid,
            "type": str(market_type),
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "meta": {}
        }
        # calculate and add flags
        flags = calculate_order_flags(hidden, close, reduce_only, post_only, oco)
        payload['flags'] = flags
        # add extra parameters
        if price_trailing != None:
            payload['price_trailing'] = price_trailing
        if price_aux_limit != None:
            payload['price_aux_limit'] = price_aux_limit
        if oco_stop_price != None:
            payload['price_oco_stop'] = str(oco_stop_price)
        if time_in_force != None:
            payload['tif'] = time_in_force
        if gid != None:
            payload['gid'] = gid
        if leverage != None:
            payload['lev'] = str(leverage)
        if aff_code != None:
            payload['meta']['aff_code'] = str(aff_code)
        # submit the order
        self.pending_orders[cid] = payload
        self._create_callback(cid, onConfirm, self.pending_order_confirm_callbacks)
        self._create_callback(cid, onClose, self.pending_order_close_callbacks)
        await self.bfxapi._send_auth_command('on', payload)
        self.logger.info("Order cid={} ({} {} @ {}) dispatched".format(
            cid, symbol, amount, price))

    async def update_order(self, orderId, price=None, amount=None, delta=None, price_aux_limit=None,
                           price_trailing=None, hidden=False, close=False, reduce_only=False,
                           post_only=False, time_in_force=None, leverage=None, onConfirm=None):
        """
        Update an existing order

        @param orderId: the id of the order that you want to update
        @param price: the price you want to buy/sell at (must be positive)
        @param amount: order size: how much you want to buy/sell,
          a negative amount indicates a sell order and positive a buy order
        @param delta:	change of amount
        @param price_trailing:	decimal trailing price
        @param price_aux_limit:	decimal	auxiliary Limit price (only for STOP LIMIT)
        @param hidden: if True, order should be hidden from orderbooks
        @param close: if True, close position if position present
        @param reduce_only: if True, ensures that the executed order does not flip the opened position
        @param post_only: if True, ensures the limit order will be added to the order book and not
          match with a pre-existing order
        @param time_in_force: datetime for automatic order cancellation ie. 2020-01-01 10:45:23
        @param leverage: the amount of leverage to apply to the order as an integer
        @param onConfirm: function called when the bitfinex websocket receives signal that the order
          was confirmed
        @param onClose: function called when the bitfinex websocket receives signal that the order
          was closed due to being filled or cancelled
        """
        self._create_callback(orderId, onConfirm, self.pending_update_confirm_callbacks)
        payload = {"id": orderId}
        if price != None:
            payload['price'] = str(price)
        if amount != None:
            payload['amount'] = str(amount)
        if delta != None:
            payload['delta'] = str(delta)
        if price_aux_limit != None:
            payload['price_aux_limit'] = str(price_aux_limit)
        if price_trailing != None:
            payload['price_trailing'] = str(price_trailing)
        if time_in_force != None:
            payload['tif'] = str(time_in_force)
        if leverage != None:
            payload['lev'] = str(leverage)
        flags = calculate_order_flags(
            hidden, close, reduce_only, post_only, False)
        payload['flags'] = flags
        await self.bfxapi._send_auth_command('ou', payload)
        self.logger.info("Update Order order_id={} dispatched".format(orderId))

    async def cancel_order(self, orderId, onConfirm=None):
        """
        Cancel an existing open order

        @param orderId: the id of the order that you want to update
        @param onConfirm: function called when the bitfinex websocket receives signal that the
                          order was confirmed
        """
        self._create_callback(orderId, onConfirm, self.pending_cancel_confirm_callbacks)
        await self.bfxapi._send_auth_command('oc', {'id': orderId})
        self.logger.info("Order cancel order_id={} dispatched".format(orderId))

    async def cancel_all_orders(self):
        """
        Cancel all existing open orders

        This function closes all open orders.
        """
        await self.bfxapi._send_auth_command('oc_multi', { 'all': 1 })

    async def cancel_order_group(self, gid, onConfirm=None):
        """
        Cancel a set of orders using a single group id.
        """
        self._create_callback(gid, onConfirm, self.pending_cancel_confirm_callbacks)
        await self.bfxapi._send_auth_command('oc_multi', { 'gid': [gid] })

    async def cancel_order_multi(self, ids=None, gids=None):
        """
        Cancel existing open orders as a batch

        @param ids: an array of order ids
        @param gids: an array of group ids
        """
        payload = {}
        if ids:
            payload['id'] = ids
        if gids:
            payload['gid'] = gids
        await self.bfxapi._send_auth_command('oc_multi', payload)

    def _create_callback(self, identifier, func, callback_storage):
        if not func:
            return
        if identifier in callback_storage:
            callback_storage[identifier] += [func]
        else:
            callback_storage[identifier] = [func]

    async def _execute_callback(self, order, callback_storage):
        idents = [order.id, order.cid, order.gid]
        tasks = []
        key = None
        for k in callback_storage.keys():
            if k in idents:
                key = k
                # call all callbacks associated with identifier
                for callback in callback_storage[k]:
                    tasks += [callback(order)]
                break
        # remove from callbacks
        if key:
            del callback_storage[key]
        await asyncio.gather(*tasks)

    def _gen_unique_cid(self):
        return gen_unique_cid()
