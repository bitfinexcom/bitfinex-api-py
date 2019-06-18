"""
Module used to house the bitfine websocket client
"""

import asyncio
import json
import time
import random

from .GenericWebsocket import GenericWebsocket, AuthError
from .SubscriptionManager import SubscriptionManager
from .WalletManager import WalletManager
from .OrderManager import OrderManager
from ..utils.auth import generate_auth_payload
from ..models import Order, Trade, OrderBook


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


class BfxWebsocket(GenericWebsocket):
    """
    More complex websocket that heavily relies on the btfxwss module.
    This websocket requires authentication and is capable of handling orders.
    https://github.com/Crypto-toolbox/btfxwss
    """

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
        10302: 'Unknown channel',
        10400: 'Subscription Failed (generic)',
        10401: 'Not subscribed',
        11000: 'Not ready, try again later',
        20000: 'User is invalid!',
        20051: 'Websocket server stopping',
        20060: 'Websocket server resyncing',
        20061: 'Websocket server resync complete'
    }

    def __init__(self, API_KEY=None, API_SECRET=None, host='wss://api-pub.bitfinex.com/ws/2',
                 manageOrderBooks=False, dead_man_switch=False, ws_capacity=25, logLevel='INFO', parse_float=float,
                 *args, **kwargs):
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.manageOrderBooks = manageOrderBooks
        self.dead_man_switch = dead_man_switch
        self.pendingOrders = {}
        self.orderBooks = {}
        self.ws_capacity = ws_capacity
        # How should we store float values? could also be bfxapi.Decimal
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
            if subscription.channel_name == 'book':
                await self._order_book_handler(data, raw_message_str)
            if subscription.channel_name == 'trades':
                await self._trade_handler(data)
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
        err_string = self.ERRORS[data.get('code', 10000)]
        err_string = "(socketId={}) {} - {}".format(
            socketId,
            self.ERRORS[data.get('code', 10000)],
            data.get("msg", ""))
        self._emit('error', err_string)

    async def _system_auth_handler(self, socketId, data):
        if data.get('status') == 'FAILED':
            raise AuthError(self.ERRORS[data.get('code')])
        else:
            self._emit('authenticated', data)
            self.logger.info("Authentication successful.")

    async def _trade_update_handler(self, data):
        tData = data[2]
        # [209, 'tu', [312372989, 1542303108930, 0.35, 5688.61834032]]
        if self.subscriptionManager.is_subscribed(data[0]):
            symbol = self.subscriptionManager.get(data[0]).symbol
            tradeObj = _parse_trade(tData, symbol)
            self._emit('new_trade', tradeObj)

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

    async def _funding_offer_snapshot_handler(self, data):
        self._emit('funding_offer_snapshot', data)
        self.logger.info("Funding offer snapshot: {}".format(data))

    async def _funding_load_snapshot_handler(self, data):
        self._emit('funding_loan_snapshot', data[2])
        self.logger.info("Funding loan snapshot: {}".format(data))

    async def _funding_credit_snapshot_handler(self, data):
        self._emit('funding_credit_snapshot', data[2])
        self.logger.info("Funding credit snapshot: {}".format(data))

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

    async def _ws_authenticate_socket(self, socketId):
        socket = self.sockets[socketId]
        socket.set_authenticated()
        jdata = generate_auth_payload(self.API_KEY, self.API_SECRET)
        if self.dead_man_switch:
            jdata['dms'] = 4
        await socket.ws.send(json.dumps(jdata))

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

    async def _send_auth_command(self, channel_name, data):
        payload = [0, channel_name, None, data]
        socket = self.get_authenticated_socket()
        if socket == None:
            raise ValueError("authenticated socket connection not found")
        if not socket.isConnected:
            raise ValueError("authenticated socket not connected")
        await socket.ws.send(json.dumps(payload))

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

    async def enable_flag(self, flag):
        payload = {
            "event": 'conf',
            "flags": flag
        }
        # enable on all sockets
        for socket in self.sockets.values():
            if socket.isConnected:
                await socket.ws.send(json.dumps(payload))

    async def subscribe(self, *args, **kwargs):
        return await self.subscriptionManager.subscribe(*args, **kwargs)

    async def unsubscribe(self, *args, **kwargs):
        return await self.subscriptionManager.unsubscribe(*args, **kwargs)

    async def resubscribe(self, *args, **kwargs):
        return await self.subscriptionManager.resubscribe(*args, **kwargs)

    async def unsubscribe_all(self, *args, **kwargs):
        return await self.subscriptionManager.unsubscribe_all(*args, **kwargs)

    async def resubscribe_all(self, *args, **kwargs):
        return await self.subscriptionManager.resubscribe_all(*args, **kwargs)

    async def submit_order(self, *args, **kwargs):
        return await self.orderManager.submit_order(*args, **kwargs)

    async def update_order(self, *args, **kwargs):
        return await self.orderManager.update_order(*args, **kwargs)

    async def cancel_order(self, *args, **kwargs):
        return await self.orderManager.cancel_order(*args, **kwargs)

    async def cancel_order_group(self, *args, **kwargs):
        return await self.orderManager.cancel_order_group(*args, **kwargs)

    async def cancel_all_orders(self, *args, **kwargs):
        return await self.orderManager.cancel_all_orders(*args, **kwargs)

    async def cancel_order_multi(self, *args, **kwargs):
        return await self.orderManager.cancel_order_multi(*args, **kwargs)
