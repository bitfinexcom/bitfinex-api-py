import json

from .GenericWebsocket import GenericWebsocket

class DataServerWebsocket(GenericWebsocket):
  '''
  Basic websocket client that simply reads data from the DataServer. This instance
  of the websocket should only ever be used in backtest mode since it isnt capable
  of handling orders.
  '''
  WS_END = 'bt.end'
  WS_CANDLE = 'bt.candle'
  WS_TRADE = 'bt.trade'
  WS_START = 'bt.start'
  WS_SYNC_START = 'bt.sync.start'
  WS_SYNC_END = 'bt.sync.end'
  WS_CONNECT = 'connected'

  def __init__(self, host='ws://localhost:8899', *args, **kwargs):
    super(DataServerWebsocket, self).__init__(host,  *args, **kwargs)

  def run(self, fromDate, toDate, syncTrades=True, syncCandles=True, tf='1m',
      candleFields='*', tradeFields='*', syncMissing=True):
    self.fromDate = fromDate
    self.toDate = toDate
    self.tf = tf
    self.sync = syncCandles
    self.syncTrades = syncTrades
    self.syncCandles = syncCandles
    self.syncMissing = syncMissing
    self.candleFields = candleFields
    self.tradeFields = tradeFields
    super(DataServerWebsocket, self).run()
  
  async def on_message(self, message):
    self.logger.debug(message)
    msg = json.loads(message)
    eType = msg[0]
    if eType == self.WS_SYNC_START:
      self.logger.info("Syncing data with backtest server, please wait...")
    elif eType == self.WS_SYNC_END:
      self.logger.info("Syncing complete.")
    elif eType == self.WS_START:
      self.logger.info("Backtest data stream starting...")
    elif eType == self.WS_END:
      self.logger.info("Backtest data stream complete.")
      await self.on_close()
    elif eType == self.WS_CANDLE:
      self._onCandle(msg)
    elif eType == self.WS_TRADE:
      self._onTrade(msg)
    elif eType == self.WS_CONNECT:
      await self.on_open()
    else:
      self.logger.warn('Unknown websocket command: {}'.format(msg[0]))
  
  def _exec_bt_string(self):
    data = '["exec.bt", [{}, {}, "{}", "{}", "{}", "{}", "{}", "{}", "{}"]]'.format(
        self.fromDate, self.toDate, self.symbol, self.tf, json.dumps(self.syncCandles),
        json.dumps(self.syncTrades), self.candleFields, self.tradeFields, json.dumps(self.sync))
    return data
  
  async def on_open(self):
    data = self._exec_bt_string()
    await self.ws.send(data)
  
  async def _onCandle(self, data):
    candle = data[3]
    await self.onCandleHook(candle)
  
  async def _onTrade(self, data):
    trade = data[2]
    await self.onTradeHook(trade)
