import asyncio
import json
import time
import hashlib
import hmac
import random

from .GenericWebsocket import GenericWebsocket, AuthError
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
    self.channels = {}
    self.API_KEY=API_KEY
    self.API_SECRET=API_SECRET
    self.manageOrderBooks = manageOrderBooks
    self.pendingOrders = {}
    self.orderBooks = {}

    super(BfxWebsocket, self).__init__(host, *args, **kwargs)

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
    elif chanId in self.channels:
      # candles do not have an event 
      if self.channels[chanId].get('channel') == 'candles':
        await self._candle_handler(data)
      if self.channels[chanId].get('channel') == 'book':
        await self._order_book_handler(data)
    else:
      self.logger.warn("Unknow data event: '{}' {}".format(dataEvent, data))

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
    chanEvent = data.get('channel')
    self.logger.info("Subscribed to channel '{}'".format(chanEvent))
    ## add channel to known list
    chanId = data.get('chanId')
    ## if is a candles subscribption, then get the symbol
    ## from the key
    if data.get('key'):
      kd = data.get('key').split(':')
      data['tf'] = kd[1]
      data['symbol'] = kd[2]

    self.channels[chanId] = data

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
    if data[0] in self.channels:
      channelData = self.channels[data[0]]
      tradeObj = _parse_trade(tData, channelData.get('symbol'))
      self._emit('new_trade', tradeObj)

  async def _trade_executed_handler(self, data):
    tData = data[2]
    # [209, 'te', [312372989, 1542303108930, 0.35, 5688.61834032]]
    if data[0] in self.channels:
      channelData = self.channels[data[0]]
      tradeObj = _parse_trade(tData, channelData.get('symbol'))
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
    # order created and executed
    # [0,"oc",[1151349678,null,1542203391995,"tBTCUSD",1542203389940,1542203389966,0,0.1,
    # "EXCHANGE MARKET",null,null,null,0,"EXECUTED @ 18922.0(0.03299997): was PARTIALLY FILLED 
    # @ 18909.0(0.06700003)",null,null,18909,18913.2899961,0,0,null,null,null,0,0,null,null,null,
    # "API>BFX",null,null,null]]
    tInfo = data[2]
    order = Order(tInfo)
    trade = Trade(order)
    self.logger.info("Order closed: {} {}".format(order.symbol, order.status))
    self._emit('order_closed', order, trade)
    if order.cId in self.pendingOrders:
      if self.pendingOrders[order.cId][0]:
        await self.pendingOrders[order.cId][0](order, trade)
      del self.pendingOrders[order.cId]
      self._emit('order_confirmed', order, trade)

  async def _order_update_handler(self, data):
    # order created but partially filled
    # [0, 'ou', [1151351581, None, 1542629457873, 'tBTCUSD', 1542629458071, 
    # 1542629458189, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE', 
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX', 
    # None, None, None]]
    tInfo = data[2]
    order = Order(tInfo)
    trade = Trade(order)
    self.logger.info("Order update: {} {}".format(order, trade))
    self._emit('order_update', order, trade)
    if order.cId in self.pendingOrders:
      if self.pendingOrders[order.cId][0]:
        await self.pendingOrders[order.cId][0](order, trade)
      del self.pendingOrders[order.cId]
      self._emit('order_confirmed', order, trade)

  async def _order_new_handler(self, data):
    # order created but not executed /  created but partially filled
    # [0, 'on', [1151351563, None, 1542624024383, 'tBTCUSD', 1542624024596,
    # 1542624024617, 0.01, 0.01, 'EXCHANGE LIMIT', None, None, None, 0, 'ACTIVE',
    # None, None, 100, 0, 0, 0, None, None, None, 0, 0, None, None, None, 'API>BFX',
    # None, None, None]]
    tInfo = data[2]
    order = Order(tInfo)
    trade = Trade(order)
    self.logger.info("Order new: {} {}".format(order, trade))
    self._emit('order_new', order, trade)
    if order.cId in self.pendingOrders:
      if self.pendingOrders[order.cId][0]:
        await self.pendingOrders[order.cId][0](order, trade)
      self._emit('order_confirmed', order, trade)
      del self.pendingOrders[order.cId]

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
    channelData = self.channels[data[0]]
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
          'symbol': channelData['symbol']
        }
        self._emit('seed_trade', trade)
    else:
      tradeObj = _parse_trade_snapshot_item(data, channelData['symbol'])
      self._emit('new_trade', tradeObj)

  async def _candle_handler(self, data):
    chanId = data[0]
    channelData = self.channels[chanId]
    if type(data[1][0]) is list:
      # Process the batch of seed candles on
      # websocket subscription
      candlesSnapshot = data[1]
      candlesSnapshot.reverse()
      for c in candlesSnapshot:
        candle = _parse_candle(c, channelData['symbol'], channelData['tf'])
        self._emit('seed_candle', candle)
    else:
      candle = _parse_candle(data[1], channelData['symbol'], channelData['tf'])
      self._emit('new_candle', candle)
  
  async def _order_book_handler(self, data):
    obInfo = data[1]
    channelData = self.channels[data[0]]
    symbol = channelData.get('symbol')
    if data[1] == "cs":
      dChecksum = data[2] & 0xffffffff # force to signed int
      checksum = self.orderBooks[symbol].checksum()
      # force checksums to signed integers
      isValid = (dChecksum) == (checksum)
      if isValid:
        self.logger.debug("Checksum orderbook validation for '{}' successful."
          .format(symbol))
      else:
        # TODO: resync with snapshot
        self.logger.warn("Checksum orderbook invalid for '{}'. Orderbook out of syc."
          .format(symbol))
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

  async def send_auth_command(self, channel_name, data):
    payload = [0, channel_name, None, data]
    await self.ws.send(json.dumps(payload))

  async def enable_flag(self, flag):
    payload = {
      "event": 'conf',
      "flags": flag
    }
    await self.ws.send(json.dumps(payload))

  def subscribe(self, channel_name, symbol, timeframe=None, **kwargs):
    q = {'event': 'subscribe', 'channel': channel_name, 'symbol': symbol}
    if timeframe:
      q['key'] = 'trade:{}:{}'.format(timeframe, symbol)
    q.update(**kwargs)
    self.logger.info("Subscribing to channel {}".format(channel_name))
    # tmp = self.ws.send(json.dumps(q))
    asyncio.ensure_future(self.ws.send(json.dumps(q)))

  async def submit_order(self, symbol, price, amount, market_type,
      hidden=False, onComplete=None, onError=None, *args, **kwargs):
    order_id = int(round(time.time() * 1000))
    # send order over websocket
    payload = {
      "cid": order_id,
      "type": str(market_type),
      "symbol": symbol,
      "amount": str(amount),
      "price": str(price)
    }
    self.pendingOrders[order_id] = (onComplete, onError)
    await self.send_auth_command('on', payload)
    self.logger.info("Order cid={} ({} {} @ {}) dispatched".format(
      order_id, symbol, amount, price))

  async def update_order(self, orderId, price=None, amount=None, delta=None,
    price_aux_limit=None, price_trailing=None, flags=None, time_in_force=None,
    onComplete=None, onError=None):
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
    self.pendingOrders[orderId] = (onComplete, onError)
    await self.send_auth_command('ou', payload)
    self.logger.info("Update Order order_id={} dispatched".format(orderId))

  async def cancel_order(self, orderId, onComplete=None, onError=None):
    self.pendingOrders[orderId] = (onComplete, onError)
    await self.send_auth_command('oc', { 'id': orderId })
    self.logger.info("Order cancel order_id={} dispatched".format(orderId))
  
  async def cancel_order_multi(self, orderIds, onComplete=None, onError=None):
    self.pendingOrders[orderIds[0]] = (onComplete, onError)
    await self.send_auth_command('oc', { 'id': orderIds })
    self.logger.info("Order cancel order_ids={} dispatched".format(orderIds))
