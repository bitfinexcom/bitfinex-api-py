"""
Module used to house the bitfine websocket client
"""

import asyncio
import json
import time
import random

from .generic_websocket import GenericWebsocket, AuthError
from .subscription_manager import SubscriptionManager
from .wallet_manager import WalletManager
from .order_manager import OrderManager
from ..utils.auth import generate_auth_payload
from ..utils.decorators import handle_failure
from ..models import Order, Trade, OrderBook, Ticker, FundingTicker


class Flags:
    """
    Enum used to index the available flags used in the authentication
    websocket packet
    """
    DEC_S = 9
    TIME_S = 32
    TIMESTAMP = 32768
    SEQ_ALL = 65536
    CHECKSUM = 131072

    strings = {
        9: 'DEC_S',
        32: 'TIME_S',
        32768: 'TIMESTAMP',
        65536: 'SEQ_ALL',
        131072: 'CHECKSUM'
    }


def _parse_candle(cData, symbol, tf):
    return {
        'mts': cData[0],
        'open': cData[1],
        'close': cData[2],
        'high': cData[3],
        'low': cData[4],
        'volume': cData[5],
        'symbol': symbol,
        'tf': tf
    }


def _parse_trade_snapshot_item(tData, symbol):
    return {
        'mts': tData[3],
        'price': tData[4],
        'amount': tData[5],
        'symbol': symbol
    }


def _parse_trade(tData, symbol):
    return {
        'mts': tData[1],
        'price': tData[3],
        'amount': tData[2],
        'symbol': symbol
    }

def _parse_deriv_status_update(sData, symbol):
    return {
            'symbol': symbol,
            'status_type': 'deriv',
            'mts': sData[0],
            # placeholder
            'deriv_price': sData[2],
            'spot_price': sData[3],
            # placeholder
            'insurance_fund_balance': sData[5],
            # placeholder
            # placeholder
            'funding_accrued': sData[8],
            'funding_step': sData[9],
            # placeholder
        }

ERRORS = {
    10000: 'Unknown event',
    10001: 'Generic error',
    10008: 'Concurrency error',
    10020: 'Request parameters error',
    10050: 'Configuration setup failed',
    10100: 'Failed authentication',
    10111: 'Error in authentication request payload',
    10112: 'Error in authentication request signature',
    10113: 'Error in authentication request encryption',
    10114: 'Error in authentication request nonce',
    10200: 'Error in un-authentication request',
    10300: 'Subscription Failed (generic)',
    10301: 'Already Subscribed',
    10305: 'Reached limit of open channels',
    10302: 'Unknown channel',
    10400: 'Subscription Failed (generic)',
    10401: 'Not subscribed',
    11000: 'Not ready, try again later',
    20000: 'User is invalid!',
    20051: 'Websocket server stopping',
    20060: 'Websocket server resyncing',
    20061: 'Websocket server resync complete'
}

class BfxWebsocket(GenericWebsocket):
    """
    More complex websocket that heavily relies on the btfxwss module.
    This websocket requires authentication and is capable of handling orders.
    https://github.com/Crypto-toolbox/btfxwss

    ### Emitter events:
    - `all` (array|Object): listen for all messages coming through
    - `connected:` () called when a connection is made
    - `disconnected`: () called when a connection is ended (A reconnect attempt may follow)
    - `stopped`: () called when max amount of connection retries is met and the socket is closed
    - `authenticated` (): called when the websocket passes authentication
    - `notification` (Notification): incoming account notification
    - `error` (array): error from the websocket
    - `order_closed` (Order, Trade): when an order has been closed
    - `order_new` (Order, Trade): when an order has been created but not closed. Note: will not be called if order is executed and filled instantly
    - `order_confirmed` (Order, Trade): When an order has been submitted and received
    - `wallet_snapshot` (array[Wallet]): Initial wallet balances (Fired once)
    - `order_snapshot` (array[Order]): Initial open orders (Fired once)
    - `positions_snapshot` (array): Initial open positions (Fired once)
    - `positions_new` (array): Initial open positions (Fired once)
    - `positions_update` (array): An active position has been updated
    - `positions_close` (array): An active position has closed
    - `wallet_update` (Wallet): Changes to the balance of wallets
    - `status_update` (Object): New platform status info
    - `seed_candle` (Object): Initial past candle to prime strategy
    - `seed_trade` (Object): Initial past trade to prime strategy
    - `funding_offer_snapshot` (array): Opening funding offer balances
    - `funding_loan_snapshot` (array): Opening funding loan balances
    - `funding_credit_snapshot` (array): Opening funding credit balances
    - `balance_update` (array): When the state of a balance is changed
    - `new_trade` (array): A new trade on the market has been executed
    - `new_ticker` (Ticker|FundingTicker): A new ticker update has been published
    - `new_funding_ticker` (FundingTicker): A new funding ticker update has been published
    - `new_trading_ticker` (Ticker): A new trading ticker update has been published
    - `trade_update` (array): A trade on the market has been updated
    - `new_candle` (array): A new candle has been produced
    - `margin_info_updates` (array): New margin information has been broadcasted
    - `funding_info_updates` (array): New funding information has been broadcasted
    - `order_book_snapshot` (array): Initial snapshot of the order book on connection
    - `order_book_update` (array): A new order has been placed into the ordebrook
    - `subscribed` (Subscription): A new channel has been subscribed to
    - `unsubscribed` (Subscription): A channel has been un-subscribed
    """

    def __init__(self, API_KEY=None, API_SECRET=None, host='wss://api-pub.bitfinex.com/ws/2',
                 manageOrderBooks=False, dead_man_switch=False, ws_capacity=25, logLevel='INFO', parse_float=float,
                 channel_filter=[], *args, **kwargs):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.manageOrderBooks = manageOrderBooks
        self.dead_man_switch = dead_man_switch
        self.orderBooks = {}
        self.ws_capacity = ws_capacity
        self.channel_filter = channel_filter
        # How should we store float values? could also be bfxapi.decimal
        # which is slower but has higher precision.
        self.parse_float = parse_float
        super(BfxWebsocket, self).__init__(host, logLevel=logLevel, *args, **kwargs)
        self.subscriptionManager = SubscriptionManager(self, logLevel=logLevel)
        self.orderManager = OrderManager(self, logLevel=logLevel)
        self.wallets = WalletManager()

        self._WS_DATA_HANDLERS = {
            'tu': self._trade_update_handler,
            'wu': self._wallet_update_handler,
            'hb': self._heart_beat_handler,
            'te': self._trade_executed_handler,
            'oc': self._order_closed_handler,
            'ou': self._order_update_handler,
            'on': self._order_new_handler,
            'os': self._order_snapshot_handler,
            'ws': self._wallet_snapshot_handler,
            'ps': self._position_snapshot_handler,
            'pu': self._position_update_handler,
            'pn': self._position_new_handler,
            'pc': self._position_close_handler,
            'fos': self._funding_offer_snapshot_handler,
            'fcs': self._funding_credit_snapshot_handler,
            'fls': self._funding_load_snapshot_handler,
            'bu': self._balance_update_handler,
            'n': self._notification_handler,
            'miu': self._margin_info_update_handler,
            'fiu': self._funding_info_update_handler
        }

        self._WS_SYSTEM_HANDLERS = {
            'info': self._system_info_handler,
            'subscribed': self._system_subscribed_handler,
            'unsubscribed': self._system_unsubscribe_handler,
            'error': self._system_error_handler,
            'auth': self._system_auth_handler,
            'conf': self._system_conf_handler
        }

    async def _ws_system_handler(self, socketId, msg):
        eType = msg.get('event')
        if eType in self._WS_SYSTEM_HANDLERS:
            await self._WS_SYSTEM_HANDLERS[eType](socketId, msg)
        else:
            self.logger.warn(
                "Unknown websocket event (socketId={}): '{}' {}".format(socketId, eType, msg))

    async def _ws_data_handler(self, socketId, data, raw_message_str):
        dataEvent = data[1]
        chan_id = data[0]

        if type(dataEvent) is str and dataEvent in self._WS_DATA_HANDLERS:
            return await self._WS_DATA_HANDLERS[dataEvent](data)
        elif self.subscriptionManager.is_subscribed(chan_id):
            subscription = self.subscriptionManager.get(chan_id)
            # candles do not have an event
            if subscription.channel_name == 'candles':
                await self._candle_handler(data)
            elif subscription.channel_name == 'book':
                await self._order_book_handler(data, raw_message_str)
            elif subscription.channel_name == 'trades':
                await self._trade_handler(data)
            elif subscription.channel_name == 'status':
                await self._status_handler(data)
            elif subscription.channel_name == 'ticker':
                await self._ticker_handler(data)
            else:
                self.logger.warn("Unknown channel type '{}'".format(subscription.channel_name))
        else:
            self.logger.warn(
                "Unknown data event: '{}' {}".format(dataEvent, data))

    async def _system_info_handler(self, socketId, data):
        self.logger.info(data)
        if data.get('serverId', None):
            # connection has been established
            await self.on_open(socketId)

    async def _system_conf_handler(self, socketId, data):
        flag = data.get('flags')
        status = data.get('status')
        if flag not in Flags.strings:
            self.logger.warn("Unknown config value set {}".format(flag))
            return
        flagString = Flags.strings[flag]
        if status == "OK":
            self.logger.info("Enabled config flag {}".format(flagString))
        else:
            self.logger.error(
                "Unable to enable config flag {}".format(flagString))

    async def _system_subscribed_handler(self, socket_id, data):
        await self.subscriptionManager.confirm_subscription(socket_id, data)

    async def _system_unsubscribe_handler(self, socket_id, data):
        await self.subscriptionManager.confirm_unsubscribe(socket_id, data)

    async def _system_error_handler(self, socketId, data):
        err_string = ERRORS[data.get('code', 10000)]
        err_string = "(socketId={}) {} - {}".format(
            socketId,
            ERRORS[data.get('code', 10000)],
            data.get("msg", ""))
        self._emit(Exception(err_string))

    async def _system_auth_handler(self, socketId, data):
        if data.get('status') == 'FAILED':
            raise AuthError(ERRORS[data.get('code')])
        else:
            self._emit('authenticated', data)
            self.logger.info("Authentication successful.")

    async def _trade_update_handler(self, data):
        tData = data[2]
        # [209, 'tu', [312372989, 1542303108930, 0.35, 5688.61834032]]
        if self.subscriptionManager.is_subscribed(data[0]):
            symbol = self.subscriptionManager.get(data[0]).symbol
            tradeObj = _parse_trade(tData, symbol)
            self._emit('trade_update', tradeObj)

    async def _trade_executed_handler(self, data):
        tData = data[2]
        # [209, 'te', [312372989, 1542303108930, 0.35, 5688.61834032]]
        if self.subscriptionManager.is_subscribed(data[0]):
            symbol = self.subscriptionManager.get(data[0]).symbol
            tradeObj = _parse_trade(tData, symbol)
            self._emit('new_trade', tradeObj)

    async def _wallet_update_handler(self, data):
        # [0,"wu",["exchange","USD",89134.66933283,0]]
        uw = self.wallets._update_from_event(data)
        self._emit('wallet_update', uw)
        self.logger.info("Wallet update: {}".format(uw))

    async def _heart_beat_handler(self, data):
        self.logger.debug("Heartbeat - {}".format(self.host))

    async def _margin_info_update_handler(self, data):
        self._emit('margin_info_update', data)
        self.logger.info("Margin info update: {}".format(data))

    async def _funding_info_update_handler(self, data):
        self._emit('funding_info_update', data)
        self.logger.info("Funding info update: {}".format(data))

    async def _notification_handler(self, data):
        nInfo = data[2]
        self._emit('notification', nInfo)
        notificationType = nInfo[6]
        notificationText = nInfo[7]
        if notificationType == 'ERROR':
            # self._emit('error', notificationText)
            await self._order_error_handler(data)
            self.logger.error(
                "Notification ERROR: {}".format(notificationText))
        else:
            self.logger.info(
                "Notification SUCCESS: {}".format(notificationText))

    async def _balance_update_handler(self, data):
        self.logger.info('Balance update: {}'.format(data[2]))
        self._emit('balance_update', data[2])

    async def _order_closed_handler(self, data):
        await self.orderManager.confirm_order_closed(data)

    async def _order_error_handler(self, data):
        await self.orderManager.confirm_order_error(data)

    async def _order_update_handler(self, data):
        await self.orderManager.confirm_order_update(data)

    async def _order_new_handler(self, data):
        await self.orderManager.confirm_order_new(data)

    async def _order_snapshot_handler(self, data):
        await self.orderManager.build_from_order_snapshot(data)

    async def _wallet_snapshot_handler(self, data):
        wallets = self.wallets._update_from_snapshot(data)
        self._emit('wallet_snapshot', wallets)

    async def _position_snapshot_handler(self, data):
        self._emit('position_snapshot', data)
        self.logger.info("Position snapshot: {}".format(data))

    async def _position_update_handler(self, data):
        self._emit('position_update', data)
        self.logger.info("Position update: {}".format(data))

    async def _position_close_handler(self, data):
        self._emit('position_close', data)
        self.logger.info("Position close: {}".format(data))

    async def _position_new_handler(self, data):
        self._emit('position_new', data)
        self.logger.info("Position new: {}".format(data))

    async def _funding_offer_snapshot_handler(self, data):
        self._emit('funding_offer_snapshot', data)
        self.logger.info("Funding offer snapshot: {}".format(data))

    async def _funding_load_snapshot_handler(self, data):
        self._emit('funding_loan_snapshot', data[2])
        self.logger.info("Funding loan snapshot: {}".format(data))

    async def _funding_credit_snapshot_handler(self, data):
        self._emit('funding_credit_snapshot', data[2])
        self.logger.info("Funding credit snapshot: {}".format(data))

    async def _status_handler(self, data):
        sub = self.subscriptionManager.get(data[0])
        symbol = sub.symbol
        status_type = sub.key.split(":")[0]
        rstatus = data[1]
        if status_type == "deriv":
            status = _parse_deriv_status_update(rstatus, symbol)
        if status:
            self._emit('status_update', status)
        else:
            self.logger.warn('Unknown status data type: {}'.format(data))

    async def _ticker_handler(self, data):
        symbol = self.subscriptionManager.get(data[0]).symbol
        if type(data[1]) is list and len(symbol) > 0:
            raw_ticker = data[1]
            t = None
            if symbol[0] == 't':
                t = Ticker.from_raw_ticker(raw_ticker, symbol)
                self._emit('new_trading_ticker', t)
            elif symbol[0] == 'f':
                t = FundingTicker.from_raw_ticker(raw_ticker, symbol)
                self._emit('new_funding_ticker', t)
            else:
                self.logger.warn('Unknown ticker type: {}'.format(raw_ticker))
            self._emit('new_ticker', t)

    async def _trade_handler(self, data):
        symbol = self.subscriptionManager.get(data[0]).symbol
        if type(data[1]) is list:
            data = data[1]
            # Process the batch of seed trades on
            # connection
            data.reverse()
            for t in data:
                trade = {
                    'mts': t[1],
                    'amount': t[2],
                    'price': t[3],
                    'symbol': symbol
                }
                self._emit('seed_trade', trade)

    async def _candle_handler(self, data):
        subscription = self.subscriptionManager.get(data[0])
        # if candle data is empty
        if data[1] == []:
            return
        if type(data[1][0]) is list:
            # Process the batch of seed candles on
            # websocket subscription
            candlesSnapshot = data[1]
            candlesSnapshot.reverse()
            for c in candlesSnapshot:
                candle = _parse_candle(
                    c, subscription.symbol, subscription.timeframe)
                self._emit('seed_candle', candle)
        else:
            candle = _parse_candle(
                data[1], subscription.symbol, subscription.timeframe)
            self._emit('new_candle', candle)

    async def _order_book_handler(self, data, orig_raw_message):
        obInfo = data[1]
        chan_id = data[0]
        subscription = self.subscriptionManager.get(data[0])
        symbol = subscription.symbol
        if data[1] == "cs":
            dChecksum = data[2] & 0xffffffff  # force to signed int
            checksum = self.orderBooks[symbol].checksum()
            # force checksums to signed integers
            isValid = (dChecksum) == (checksum)
            if isValid:
                msg = "Checksum orderbook validation for '{}' successful."
                self.logger.debug(msg.format(symbol))
            else:
                msg = "Checksum orderbook invalid for '{}'. Resetting subscription."
                self.logger.warn(msg.format(symbol))
                # re-build orderbook with snapshot
                await self.subscriptionManager.resubscribe(chan_id)
            return
        if obInfo == []:
            self.orderBooks[symbol] = OrderBook()
            return
        isSnapshot = type(obInfo[0]) is list
        if isSnapshot:
            self.orderBooks[symbol] = OrderBook()
            self.orderBooks[symbol].update_from_snapshot(obInfo, orig_raw_message)
            self._emit('order_book_snapshot', {
                       'symbol': symbol, 'data': obInfo})
        else:
            self.orderBooks[symbol].update_with(obInfo, orig_raw_message)
            self._emit('order_book_update', {'symbol': symbol, 'data': obInfo})

    async def on_message(self, socketId, message):
        self.logger.debug(message)
        # convert float values to decimal
        msg = json.loads(message, parse_float=self.parse_float)
        self._emit('all', msg)
        if type(msg) is dict:
            # System messages are received as json
            await self._ws_system_handler(socketId, msg)
        elif type(msg) is list:
            # All data messages are received as a list
            await self._ws_data_handler(socketId, msg, message)
        else:
            self.logger.warn('Unknown (socketId={}) websocket response: {}'.format(socketId, msg))

    @handle_failure
    async def _ws_authenticate_socket(self, socketId):
        socket = self.sockets[socketId]
        socket.set_authenticated()
        jdata = generate_auth_payload(self.API_KEY, self.API_SECRET)
        if self.dead_man_switch:
            jdata['dms'] = 4
        if len(self.channel_filter) > 0:
            jdata['filter'] = self.channel_filter
        await socket.send(json.dumps(jdata))

    async def on_open(self, socket_id):
        self.logger.info("Websocket opened.")
        if len(self.sockets) == 1:
            ## only call on first connection
            self._emit('connected')
        # Orders are simulated in backtest mode
        if self.API_KEY and self.API_SECRET and self.get_authenticated_socket() == None:
            await self._ws_authenticate_socket(socket_id)
        # enable order book checksums
        if self.manageOrderBooks:
            await self.enable_flag(Flags.CHECKSUM)
        # set any existing subscriptions to not subscribed
        self.subscriptionManager.set_unsubscribed_by_socket(socket_id)
        # re-subscribe to existing channels
        await self.subscriptionManager.resubscribe_by_socket(socket_id)

    @handle_failure
    async def _send_auth_command(self, channel_name, data):
        payload = [0, channel_name, None, data]
        socket = self.get_authenticated_socket()
        if socket == None:
            raise ValueError("authenticated socket connection not found")
        if not socket.isConnected:
            raise ValueError("authenticated socket not connected")
        await socket.send(json.dumps(payload))

    def get_orderbook(self, symbol):
        return self.orderBooks.get(symbol, None)

    def get_socket_capacity(self, socket_id):
        return self.ws_capacity - self.subscriptionManager.get_sub_count_by_socket(socket_id)

    def get_most_available_socket(self):
        bestId = None
        bestCount = 0
        for socketId in self.sockets:
            cap = self.get_socket_capacity(socketId)
            if bestId == None or cap > bestCount:
                bestId = socketId
                bestCount = cap
        return self.sockets[socketId]

    def get_total_available_capcity(self):
        total = 0
        for socketId in self.sockets:
            total += self.get_socket_capacity(socketId)
        return total

    @handle_failure
    async def enable_flag(self, flag):
        """
        Enable flag on websocket connection

        # Attributes
        flag (int): int flag value
        """
        payload = {
            "event": 'conf',
            "flags": flag
        }
        # enable on all sockets
        for socket in self.sockets.values():
            if socket.isConnected:
                await socket.send(json.dumps(payload))

    async def subscribe_order_book(self, symbol):
        """
        Subscribe to an orderbook data feed

        # Attributes
        @param symbol: the trading symbol i.e 'tBTCUSD'
        """
        return await self.subscribe('book', symbol)

    async def subscribe_candles(self, symbol, timeframe):
        """
        Subscribe to a candle data feed

        # Attributes
        @param symbol: the trading symbol i.e 'tBTCUSD'
        @param timeframe: resolution of the candle i.e 15m, 1h
        """
        return await self.subscribe('candles', symbol, timeframe=timeframe)

    async def subscribe_trades(self, symbol):
        """
        Subscribe to a trades data feed

        # Attributes
        @param symbol: the trading symbol i.e 'tBTCUSD'
        """
        return await self.subscribe('trades', symbol)

    async def subscribe_ticker(self, symbol):
        """
        Subscribe to a ticker data feed

        # Attributes
        @param symbol: the trading symbol i.e 'tBTCUSD'
        """
        return await self.subscribe('ticker', symbol)

    async def subscribe_derivative_status(self, symbol):
        """
        Subscribe to a status data feed

        # Attributes
        @param symbol: the trading symbol i.e 'tBTCUSD'
        """
        key = 'deriv:{}'.format(symbol)
        return await self.subscribe('status', symbol, key=key)

    async def subscribe(self, *args, **kwargs):
        """
        Subscribe to a new channel

        # Attributes
        @param channel_name: the name of the channel i.e 'books', 'candles'
        @param symbol: the trading symbol i.e 'tBTCUSD'
        @param timeframe: sepecifies the data timeframe between each candle (only required
          for the candles channel)
        """
        return await self.subscriptionManager.subscribe(*args, **kwargs)

    async def unsubscribe(self, *args, **kwargs):
        """
        Unsubscribe from the channel with the given chanId

        # Attributes
        @param onComplete: function called when the bitfinex websocket responds with
          a signal that confirms the subscription has been unsubscribed to
        """
        return await self.subscriptionManager.unsubscribe(*args, **kwargs)

    async def resubscribe(self, *args, **kwargs):
        """
        Unsubscribes and then subscribes to the channel with the given Id

        This function is mostly used to force the channel to produce a fresh snapshot.
        """
        return await self.subscriptionManager.resubscribe(*args, **kwargs)

    async def unsubscribe_all(self, *args, **kwargs):
        """
        Unsubscribe from all channels.
        """
        return await self.subscriptionManager.unsubscribe_all(*args, **kwargs)

    async def resubscribe_all(self, *args, **kwargs):
        """
        Unsubscribe and then subscribe to all channels
        """
        return await self.subscriptionManager.resubscribe_all(*args, **kwargs)

    async def submit_order(self, *args, **kwargs):
        """
        Submit a new order

        # Attributes
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

        @param time_in_force:	datetime for automatic order cancellation ie. 2020-01-01 10:45:23
        @param leverage: the amount of leverage to apply to the order as an integer
        @param onConfirm: function called when the bitfinex websocket receives signal that the order
          was confirmed
        @param onClose: function called when the bitfinex websocket receives signal that the order
          was closed due to being filled or cancelled
        """
        return await self.orderManager.submit_order(*args, **kwargs)

    async def update_order(self, *args, **kwargs):
        """
        Update an existing order

        # Attributes
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
        return await self.orderManager.update_order(*args, **kwargs)

    async def cancel_order(self, *args, **kwargs):
        """
        Cancel an existing open order

        # Attributes
        @param orderId: the id of the order that you want to update
        @param onConfirm: function called when the bitfinex websocket receives signal that the
                          order
          was confirmed
        @param onClose: function called when the bitfinex websocket receives signal that the order
          was closed due to being filled or cancelled
        """
        return await self.orderManager.cancel_order(*args, **kwargs)

    async def cancel_order_group(self, *args, **kwargs):
        """
        Cancel a set of orders using a single group id.
        """
        return await self.orderManager.cancel_order_group(*args, **kwargs)

    async def cancel_all_orders(self, *args, **kwargs):
        """
        Cancel all existing open orders

        This function closes all open orders.
        """
        return await self.orderManager.cancel_all_orders(*args, **kwargs)

    async def cancel_order_multi(self, *args, **kwargs):
        """
        Cancel existing open orders as a batch

        # Attributes
        @param ids: an array of order ids
        @param gids: an array of group ids
        """
        return await self.orderManager.cancel_order_multi(*args, **kwargs)
