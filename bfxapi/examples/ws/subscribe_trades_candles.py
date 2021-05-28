import os
import sys
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG'
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('new_candle')
def log_candle(candle, data):
  print ("New candle: {}".format(candle))

@bfx.ws.on('new_trade')
def log_trade(trade, data):
  print ("New trade: {}".format(trade))

async def start():
  await bfx.ws.subscribe('candles', 'tBTCUSD', timeframe='1m')
  await bfx.ws.subscribe('trades', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
