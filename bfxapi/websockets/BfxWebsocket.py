import asyncio
import json
import time
import hashlib
import hmac
import random

from .GenericWebsocket import GenericWebsocket, AuthError
from .SubscriptionManager import SubscriptionManager
from .OrderManager import OrderManager
from ..models import Order, Trade, OrderBook

class Flags:
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
  '''
  More complex websocket that heavily relies on the btfxwss module. This websocket requires
  authentication and is capable of handling orders.
  https://github.com/Crypto-toolbox/btfxwss

  Translation names:

  translation table for channel names:
    Data Channels
    os      -   Orders
    hos     -   Historical Orders
    ps      -   Positions
    hts     -   Trades (snapshot)
    te      -   Trade Executed
    tu      -   Trade Execution update
    ws      -   Wallets
    bu      -   Balance Info
    miu     -   Margin Info
    fiu     -   Funding Info
    fos     -   Offers
    hfos    -   Historical Offers
    fcs     -   Credits
    hfcs    -   Historical Credits
    fls     -   Loans
    hfls    -   Historical Loans
    htfs    -   Funding Trades
    n       -   Notifications (WIP)

  Events:
    - all: listen for all messages coming through
    - connected: called when a connection is made
    - authenticated: called when the websocket passes authentication
    - notification (array): incoming account notification
    - error (string): error from the websocket
    - order_closed (Order, Trade): when an order has been closed
    - order_new (Order, Trade): when an order has been created but not closed. Note: will
        not be called if order is executed and filled instantly
    - order_confirmed (Order, Trade): when an order has been submitted and received
    - wallet_snapshot (string): Initial wallet balances (Fired once)
    - order_snapshot (string): Initial open orders (Fired once)
    - positions_snapshot (string): Initial open positions (Fired once)
    - wallet_update (string): changes to the balance of wallets
    - seed_candle (candleArray): initial past candle to prime strategy
    - seed_trade (tradeArray): initial past trade to prime strategy
    - funding_offer_snapshot:
    - funding_loan_snapshot:
    - funding_credit_snapshot:
    - balance_update when the state of a balance is changed
    - new_trade: a new trade on the market has been executed
    - new_candle: a new candle has been produced
    - margin_info_update: new margin information has been broadcasted
    - funding_info_update: new funding information has been broadcasted
  '''

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

  def __init__(self, API_KEY=None, API_SECRET=None, host='wss://api.bitfinex.com/ws/2',
      onSeedCandleHook=None, onSeedTradeHook=None, manageOrderBooks=False, *args, **kwargs):
    self.API_KEY=API_KEY
    self.API_SECRET=API_SECRET
    self.manageOrderBooks = manageOrderBooks
    self.pendingOrders = {}
    self.orderBooks = {}

    super(BfxWebsocket, self).__init__(host, *args, **kwargs)
    self.subscriptionManager = SubscriptionManager(self)
    self.orderManager = OrderManager(self)

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

  async def _ws_system_handler(self, msg):
    eType = msg.get('event')
    if eType in self._WS_SYSTEM_HANDLERS:
      await self._WS_SYSTEM_HANDLERS[eType](msg)
    else:
      self.logger.warn("Unknown websocket event: '{}' {}".format(eType, msg))

  async def _ws_data_handler(self, data):
    dataEvent = data[1]
    chanId = data[0]
    
    if type(dataEvent) is str and dataEvent in self._WS_DATA_HANDLERS:
      return await self._WS_DATA_HANDLERS[dataEvent](data)
    elif self.subscriptionManager.is_subscribed(chanId):
      subscription = self.subscriptionManager.get(chanId)
      # candles do not have an event 
      if subscription.channel_name == 'candles':
        await self._candle_handler(data)
      if subscription.channel_name == 'book':
        await self._order_book_handler(data)
    else:
      self.logger.warn("Unknown data event: '{}' {}".format(dataEvent, data))

  async def _system_info_handler(self, data):
    self.logger.info(data)
    if data.get('serverId', None):
      ## connection has been established
      await self.on_open()
  
  async def _system_conf_handler(self, data):
    flag = data.get('flags')
    status = data.get('status')
    if flag not in Flags.strings:
      self.logger.warn("Unknown config value set {}".format(flag))
      return
    flagString = Flags.strings[flag]
    if status == "OK":
      self.logger.info("Enabled config flag {}".format(flagString))
    else:
      self.logger.error("Unable to enable config flag {}".format(flagString))

  async def _system_subscribed_handler(self, data):
    await self.subscriptionManager.confirm_subscription(data)

  async def _system_unsubscribe_handler(self, data):
    await self.subscriptionManager.confirm_unsubscribe(data)

  async def _system_error_handler(self, data):
    self._emit('error', data)

  async def _system_auth_handler(self, data):
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
    wu = data[2]
    self._emit('wallet_update', data)
    self.logger.info("Wallet update: {}({}) = {}".format(wu[1], wu[0], wu[2]))

  async def _heart_beat_handler(self, data):
    self.logger.debug("Heartbeat - {}".format(self.host))

  async def _margin_info_update_handler(self, data):
    self._emit('margin_info_update', data)
    self.logger.info("Margin info update: {}".format(data))

  async def _funding_info_update_handler(self, data):
    self._emit('funding_info_update', data)
    self.logger.info("Funding info update: {}".format(data))

  async def _notification_handler(self, data):
    # [0, 'n', [1542289340429, 'on-req', None, None, 
    # [1151350600, None, 1542289341196, 'tBTCUSD', None, None, 0.01, None, 'EXCHANGE MARKET', 
    # None, None, None, None, None, None, None, 18970, None, 0, 0, None, None, None, 0, None, 
    # None, None, None, None, None, None, None], None, 'SUCCESS', 'Submitting exchange market buy order for 0.01 BTC.']]
    nInfo = data[2]
    self._emit('notification', nInfo)
    notificationType = nInfo[6]
    notificationText = nInfo[7]
    if notificationType == 'ERROR':
      self._emit('error', notificationText)
      self.logger.error("Notification ERROR: {}".format(notificationText))
    else:
      self.logger.info("Notification SUCCESS: {}".format(notificationText))

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
    self._emit('order_snapshot', data)
    self.logger.info("Position snapshot: {}".format(data))
  
  async def _wallet_snapshot_handler(self, data):
    self._emit('wallet_snapshot', data[2])
    self.logger.info("Wallet snapshot: {}".format(data))
  
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
          'price': t[2],
          'amount': t[3],
          'symbol': symbol
        }
        self._emit('seed_trade', trade)
    else:
      tradeObj = _parse_trade_snapshot_item(data, symbol)
      self._emit('new_trade', tradeObj)

  async def _candle_handler(self, data):
    subscription = self.subscriptionManager.get(data[0])
    if type(data[1][0]) is list:
      # Process the batch of seed candles on
      # websocket subscription
      candlesSnapshot = data[1]
      candlesSnapshot.reverse()
      for c in candlesSnapshot:
        candle = _parse_candle(c, subscription.symbol, subscription.timeframe)
        self._emit('seed_candle', candle)
    else:
      candle = _parse_candle(data[1], subscription.symbol, subscription.timeframe)
      self._emit('new_candle', candle)
  
  async def _order_book_handler(self, data):
    obInfo = data[1]
    chanId = data[0]
    subscription = self.subscriptionManager.get(data[0])
    symbol = subscription.symbol
    if data[1] == "cs":
      dChecksum = data[2] & 0xffffffff # force to signed int
      checksum = self.orderBooks[symbol].checksum()
      # force checksums to signed integers
      isValid = (dChecksum) != (checksum)
      if isValid:
        self.logger.debug("Checksum orderbook validation for '{}' successful."
          .format(symbol))
      else:
        self.logger.warn("Checksum orderbook invalid for '{}'. Resetting subscription."
          .format(symbol))
        # re-build orderbook with snapshot
        await self.subscriptionManager.resubscribe(chanId)
      return
    isSnapshot = type(obInfo[0]) is list
    if isSnapshot:
      self.orderBooks[symbol] = OrderBook()
      self.orderBooks[symbol].updateFromSnapshot(obInfo)
      self._emit('order_book_snapshot', { 'symbol': symbol, 'data': obInfo })
    else:
      self.orderBooks[symbol].updateWith(obInfo)
      self._emit('order_book_update', { 'symbol': symbol, 'data': obInfo })

  async def on_message(self, message):
    self.logger.debug(message)
    msg = json.loads(message)
    self._emit('all', msg)
    if type(msg) is dict:
      # System messages are received as json
      await self._ws_system_handler(msg)
    elif type(msg) is list:
      # All data messages are received as a list
      await self._ws_data_handler(msg)
    else:
      self.logger.warn('Unknown websocket response: {}'.format(msg))

  async def _ws_authenticate_socket(self):
    nonce = int(round(time.time() * 1000000))
    authMsg = 'AUTH{}'.format(nonce)
    secret = self.API_SECRET.encode()
    sig = hmac.new(secret, authMsg.encode(), hashlib.sha384).hexdigest()
    hmac.new(secret, self.API_SECRET.encode('utf'), hashlib.sha384).hexdigest()
    jdata = {
      'apiKey': self.API_KEY,
      'authSig': sig,
      'authNonce': nonce,
      'authPayload': authMsg,
      'event': 'auth'
    }
    await self.ws.send(json.dumps(jdata))

  async def on_open(self):
    self.logger.info("Websocket opened.")
    self._emit('connected')
    # Orders are simulated in backtest mode
    if self.API_KEY and self.API_SECRET:
      await self._ws_authenticate_socket()
    # enable order book checksums
    if self.manageOrderBooks:
      await self.enable_flag(Flags.CHECKSUM)

  async def _send_auth_command(self, channel_name, data):
    payload = [0, channel_name, None, data]
    await self.ws.send(json.dumps(payload))

  async def enable_flag(self, flag):
    payload = {
      "event": 'conf',
      "flags": flag
    }
    await self.ws.send(json.dumps(payload))

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
  
  async def cancel_order_multi(self, *args, **kwargs):
    return await self.cancel_order_multi(*args, **kwargs)
