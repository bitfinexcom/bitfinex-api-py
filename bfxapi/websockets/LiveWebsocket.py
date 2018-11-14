import asyncio
import json
import time
import hashlib
import hmac
import random

from .GenericWebsocket import GenericWebsocket, AuthError

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

def _parse_trade(tData, symbol):
  print (tData)
  return {
    'mts': tData[3],
    'price': tData[4],
    'amount': tData[5],
    'symbol': symbol
  }

class LiveBfxWebsocket(GenericWebsocket):
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
    te      -   Trade Event
    tu      -   Trade Update
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

  def __init__(self, API_KEY=None, API_SECRET=None, backtest=False, host='wss://test.bitfinex.com/ws',
      onSeedCandleHook=None, onSeedTradeHook=None, *args, **kwargs):
    self.channels = {}
    self.tf = '1m'
    if not onSeedCandleHook:
      raise KeyError("Expected `onSeedCandleHook` in parameters.")
    if not onSeedTradeHook:
      raise KeyError("Expected `onSeedTradeHook` in parameters.")

    self.onSeedCandleHook = onSeedCandleHook
    self.onSeedTradeHook = onSeedTradeHook
    self.API_KEY=API_KEY
    self.API_SECRET=API_SECRET
    self.backtest=backtest
    self.pendingOrders = {}

    super(LiveBfxWebsocket, self).__init__(host, *args, **kwargs)

    self._WS_DATA_HANDLERS = {
      'tu': self._trade_update_handler,
      'wu': self._wallet_update_handler,
      'hb': self._heart_beat_handler,
      'te': self._trade_event_handler,
      'oc': self._order_confirmed_handler,
      'os': self._order_snapshot_handler,
      'ws': self._wallet_snapshot_handler,
      'ps': self._position_snapshot_handler
    }

    self._WS_SYSTEM_HANDLERS = {
      'info': self._system_info_handler,
      'subscribed': self._system_subscribed_handler,
      'error': self._system_error_handler,
      'auth': self._system_auth_handler
    }

  async def _ws_system_handler(self, msg):
    eType = msg.get('event')
    if eType in self._WS_SYSTEM_HANDLERS:
      await self._WS_SYSTEM_HANDLERS[eType](msg)
    else:
      self.logger.warn('Unknown websocket event: {}'.format(eType))

  async def _ws_data_handler(self, data):
    dataEvent = data[1]
    chanId = data[0]
    
    if type(dataEvent) is str and dataEvent in self._WS_DATA_HANDLERS:
      return await self._WS_DATA_HANDLERS[dataEvent](data)
    elif chanId in self.channels:
      if self.channels[chanId] == 'trades':
        await self._trade_handler(data)
      elif self.channels[chanId] == 'candles':
        candle = data[1]
        await self._candle_handler(candle)
    else:
      self.logger.warn("Unknow data event: {}".format(dataEvent))

  async def _system_info_handler(self, data):
    self.logger.info(data)
    if data.get('serverId', None):
      ## connection has been established
      await self.on_open()

  async def _system_subscribed_handler(self, data):
    chanEvent = data.get('channel')
    self.logger.info("Subscribed to channel '{}'".format(chanEvent))
    ## add channel to known list
    chanId = data.get('chanId')
    self.channels[chanId] = chanEvent

  async def _system_error_handler(self, data):
    code = data.get('code')
    if code in self.ERRORS:
      raise Exception(self.ERRORS[code])
    else:
      raise Exception(data)

  async def _system_auth_handler(self, data):
    if data.get('status') == 'FAILED':
      raise AuthError(self.ERRORS[data.get('code')])
    else:
      self.logger.info("Authentication successful.")

  async def _trade_update_handler(self, data):
    pass
  
  async def _wallet_update_handler(self, data):
    # [0,"wu",["exchange","USD",89134.66933283,0]]
    wu = data[2]
    self.logger.info("Wallet update: {}({}) = {}".format(wu[1], wu[0], wu[2]))

  async def _heart_beat_handler(self, data):
    self.logger.debug("Heartbeat - {}".format(self.host))

  async def _trade_event_handler(self, data):
    pass

  async def _order_confirmed_handler(self, data):
    # [0,"oc",[1151345759,"BTCUSD",0,-0.1,"EXCHANGE MARKET",
    # "EXECUTED @ 16956.0(-0.05): was PARTIALLY FILLED @ 17051.0(-0.05)"
    # ,17051,17003.5,"2018-11-13T14:54:29Z",0,0,0]]
    tInfo = data[2]
    self.logger.info("Order status: {} {}".format(tInfo[1], tInfo[5]))

  async def _order_snapshot_handler(self, data):
    self.logger.info("Position snapshot update: {}".format(data))
  
  async def _wallet_snapshot_handler(self, data):
    self.logger.info("Wallet snapshot update: {}".format(data))
  
  async def _position_snapshot_handler(self, data):
    self.logger.info("Position snapshot update: {}".format(data))
  
  async def _trade_handler(self, data):
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
          'symbol': self.symbol
        }
        self.onSeedTradeHook(trade)
    else:
      tradeObj = _parse_trade(data, self.symbol)
      await self.onTradeHook(tradeObj)

  async def _candle_handler(self, data):
    if type(data[0]) is list:
      # Process the batch of seed candles on
      # websocket subscription
      data.reverse()
      for c in data:
        candle = _parse_candle(c, self.symbol, self.tf)
        self.onSeedCandleHook(candle)
    else:
      candle = _parse_candle(data, self.symbol, self.tf)
      await self.onCandleHook(candle)

  async def on_message(self, message):
    self.logger.info(message)
    msg = json.loads(message)
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
    # Orders are simulated in backtest mode
    if not self.backtest:
      await self._ws_authenticate_socket()
    # subscribe to data feed
    # TODO: allow for multiple subscriptions
    await self._subscribe('trades', symbol=self.symbol)
    key = 'trade:1m:{}'.format(self.symbol)
    await self._subscribe('candles', key=key, symbol=self.symbol)

  async def send_auth_command(self, channel_name, data):
    payload = [0, channel_name, None, data]
    await self.ws.send(json.dumps(payload))  
    print ("Order sent")
    print (json.dumps(payload))

  async def _subscribe(self, channel_name, **kwargs):
    q = {'event': 'subscribe', 'channel': channel_name}
    q.update(**kwargs)
    self.logger.info("Subscribing to channel {}".format(channel_name))
    await self.ws.send(json.dumps(q))

  async def submit_order(self, symbol, price, amount, mtsCreate, market_type,
      hidden=False, *args, **kwargs):
    order_id = random.randint(1,999999999)
    # send order over websocket
    payload = {
      "cid": order_id,
      "type": market_type,
      "symbol": symbol,
      "amount": str(amount),
      "price": str(price),
      "hidden": 1 if hidden else 0
    }
    self.pendingOrders[order_id] = payload
    await self.send_auth_command('on', payload)
    # wait for order confirmation
    # while True:
    #   message = await websocket.recv()
