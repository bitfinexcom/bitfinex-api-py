import sys
sys.path.append('../../../')

from bfxapi import Client, PUB_WS_HOST, PUB_REST_HOST

# Retrieving trades/candles requires public hosts
bfx = Client(
  logLevel='DEBUG',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('new_candle')
def log_candle(candle):
  print ("New candle: {}".format(candle))

@bfx.ws.on('new_trade')
def log_trade(trade):
  print ("New trade: {}".format(trade))

@bfx.ws.on('new_user_trade')
def log_user_trade(trade):
  print ("New user trade: {}".format(trade))

async def start():
  await bfx.ws.subscribe('candles', 'tBTCUSD', timeframe='1m')
  await bfx.ws.subscribe('trades', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
