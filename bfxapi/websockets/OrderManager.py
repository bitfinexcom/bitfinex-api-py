import time
import asyncio

from ..utils.CustomLogger import CustomLogger
from ..models import Order

class OrderManager:

  def __init__(self, bfxapi, logLevel='INFO'):
    self.bfxapi = bfxapi
    self.pending_orders = {}
    self.pending_callbacks = {}
    self.closed_orders = {}
    self.open_orders = {}
    self.logger = CustomLogger('BfxOrderManager', logLevel=logLevel)

  def get_open_orders(self):
    return list(self.open_orders.values())

  def get_closed_orders(self):
    return list(self.closed_orders.values())

  def get_pending_orders(self):
    return list(self.pending_orders.values())

  async def _confirm_order(self, order, isClosed=False):
    '''
    Called once when we first recieve infomation back from the bitfinex api
    that the order has been accepted.
    '''
    if order.cId in self.pending_orders:
      if self.pending_callbacks[order.cId][0]:
        # call onConfirm callback
        await self.pending_callbacks[order.cId][0](order)
        if isClosed:
          await self.pending_callbacks[order.cId][1](order)
          del self.pending_callbacks[order.cId]
      order.set_confirmed()
      # remove from pending orders list
      del self.pending_orders[order.cId]
      self.bfxapi._emit('order_confirmed', order)

  async def confirm_order_closed(self, raw_ws_data):
    # order created and executed
    # [0,"oc",[1151349678,null,1542203391995,"tBTCUSD",1542203389940,1542203389966,0,0.1,
    # "EXCHANGE MARKET",null,null,null,0,"EXECUTED @ 18922.0(0.03299997): was PARTIALLY FILLED 
    # @ 18909.0(0.06700003)",null,null,18909,18913.2899961,0,0,null,null,null,0,0,null,null,null,
    # "API>BFX",null,null,null]]
    order = Order.from_raw_order(raw_ws_data[2])
    order.set_open_state(False)
    if order.id in self.open_orders:
      del self.open_orders[order.id]
    await self._confirm_order(order, isClosed=True)
    self.logger.info("Order closed: {} {}".format(order.symbol, order.status))
    self.bfxapi._emit('order_closed', order)

  async def build_from_order_snapshot(self, raw_ws_data):
    '''
    Rebuild the user orderbook based on an incoming snapshot
    '''
    osData = raw_ws_data[2]
    self.open_orders = {}
    for raw_order in osData:
      order = Order.from_raw_order(raw_ws_data[2])
      order.set_open_state(True)
      self.open_orders[order.id] = order
    self.bfxapi._emit('order_snapshot', self.get_open_orders())

  async def confirm_order_update(self, raw_ws_data):
    # order created but partially filled
    # [0, 'ou', [1151351581, None, 1542629457873, 'tBTCUSD', 1542629458071, 
    # 1542629458189, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE', 
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX', 
    # None, None, None]]
    order = Order.from_raw_order(raw_ws_data[2])
    order.set_open_state(True)
    self.open_orders[order.id] = order
    await self._confirm_order(order)
    self.logger.info("Order update: {}".format(order))
    self.bfxapi._emit('order_update', order)

  async def confirm_order_new(self, raw_ws_data):
    # order created but not executed /  created but partially filled
    # [0, 'on', [1151351563, None, 1542624024383, 'tBTCUSD', 1542624024596,
    # 1542624024617, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE',
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX',
    # None, None, None]]
    order = Order.from_raw_order(raw_ws_data[2])
    order.set_open_state(True)
    self.open_orders[order.id] = order
    await self._confirm_order(order)
    self.logger.info("Order new: {}".format(order))
    self.bfxapi._emit('order_new', order)

  def _gen_unqiue_cid(self):
    return int(round(time.time() * 1000))

  async def submit_order(self, symbol, price, amount, market_type=Order.Type.LIMIT,
      hidden=False, price_trailing=None, price_aux_limit=None, oco_stop_price=None,
      close=False, reduce_only=False, post_only=False, oco=False, time_in_force=None,
      onConfirm=None, onClose=None, *args, **kwargs):
    """
    Submit a new order

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

    @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
    @param onConfirm: function called when the bitfinex websocket receives signal that the order
      was confirmed
    @param onClose: function called when the bitfinex websocket receives signal that the order
      was closed due to being filled or cancelled
    """
    cId = self._gen_unqiue_cid()
    # create base payload with required data
    payload = {
      "cid": cId,
      "type": str(market_type),
      "symbol": symbol,
      "amount": str(amount),
      "price": str(price),
    }
    # caclulate and add flags
    flags = self._calculate_flags(hidden, close, reduce_only, post_only, oco)
    payload['flags'] = flags
    # add extra parameters
    if (price_trailing):
      payload['price_trailing'] = price_trailing
    if (price_aux_limit):
      payload['price_aux_limit'] = price_aux_limit
    if (oco_stop_price):
      payload['price_oco_stop'] = oco_stop_price
    if (time_in_force):
      payload['tif'] = time_in_force
    # submit the order
    self.pending_orders[cId] = payload
    self.pending_callbacks[cId] = (onConfirm, onClose)
    await self.bfxapi._send_auth_command('on', payload)
    self.logger.info("Order cid={} ({} {} @ {}) dispatched".format(
      cId, symbol, amount, price))

  async def update_order(self, orderId, price=None, amount=None, delta=None, price_aux_limit=None,
      price_trailing=None, hidden=False, close=False, reduce_only=False, post_only=False,
      time_in_force=None, onConfirm=None, onClose=None):
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
    @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
    @param onConfirm: function called when the bitfinex websocket receives signal that the order
      was confirmed
    @param onClose: function called when the bitfinex websocket receives signal that the order
      was closed due to being filled or cancelled
    """
    order = self.open_orders[orderId]
    self.pending_callbacks[order.cId] = (onConfirm, onClose)
    payload = { "id": orderId }
    if price is not None:
      payload['price'] = str(price)
    if amount is not None:
      payload['amount'] = str(amount)
    if delta is not None:
      payload['delta'] = str(delta)
    if price_aux_limit is not None:
      payload['price_aux_limit'] = str(price_aux_limit)
    if price_trailing is not None:
      payload['price_trailing'] = str(price_trailing)
    if time_in_force is not None:
      payload['time_in_force'] = str(time_in_force)
    flags = self._calculate_flags(hidden, close, reduce_only, post_only, False)
    payload['flags'] = flags
    await self.bfxapi._send_auth_command('ou', payload)
    self.logger.info("Update Order order_id={} dispatched".format(orderId))

  async def cancel_order(self, orderId, onConfirm=None, onClose=None):
    if orderId not in self.open_orders:
      raise Exception("Order id={} is not open".format(orderId))
    order = self.open_orders[orderId]
    self.pending_callbacks[order.cId] = (onConfirm, onClose)
    await self._cancel_order(orderId)
    self.logger.info("Order cancel order_id={} dispatched".format(orderId))

  async def cancel_all_orders(self):
    ids = [self.open_orders[x].id for x in self.open_orders]
    await self.cancel_order_multi(ids)

  async def cancel_order_multi(self, orderIds):
    task_batch = []
    for oid in orderIds:
      task_batch += [
        asyncio.ensure_future(self.open_orders[oid].close())
      ]
    await asyncio.wait(*[ task_batch ])

  async def _cancel_order(self, orderId):
    await self.bfxapi._send_auth_command('oc', { 'id': orderId })

  async def _update(self, orderId, price=None, amount=None, delta=None, price_aux_limit=None,
      price_trailing=None, flags=None, time_in_force=None):
    payload = { "id": orderId }
    if price is not None:
      payload['price'] = str(price)
    if amount is not None:
      payload['amount'] = str(amount)
    if delta is not None:
      payload['delta'] = str(delta)
    if price_aux_limit is not None:
      payload['price_aux_limit'] = str(price_aux_limit)
    if price_trailing is not None:
      payload['price_trailing'] = str(price_trailing)
    if flags is not None:
      payload['flags'] = str(flags)
    if time_in_force is not None:
      payload['time_in_force'] = str(time_in_force)
    await self.bfxapi._send_auth_command('ou', payload)

  def _calculate_flags(self, hidden, close, reduce_only, post_only, oco):
    flags = 0
    flags = flags + Order.Flags.HIDDEN if hidden else flags
    flags = flags + Order.Flags.CLOSE if close else flags
    flags = flags + Order.Flags.REDUUCE_ONLY if reduce_only else flags
    flags = flags + Order.Flags.POST_ONLY if post_only else flags
    flags = flags + Order.Flags.OCO if oco else flags
    return flags
