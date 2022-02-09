import os
import sys
sys.path.append('../../../')

from bfxapi import Client, WSEvents, WSChannels

bfx = Client(
  logLevel='DEBUG'
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on(WSEvents.NEW_CANDLE)
def log_candle(candle):
  print ("New candle: {}".format(candle))

@bfx.ws.on(WSEvents.NEW_TRADE)
def log_trade(trade):
  print ("New trade: {}".format(trade))

@bfx.ws.on(WSEvents.NEW_USER_TRADE)
def log_user_trade(trade):
  print ("New user trade: {}".format(trade))

async def start():
  await bfx.ws.subscribe(WSChannels.CANDLES, 'tBTCUSD', timeframe='1m')
  await bfx.ws.subscribe(WSChannels.TRADES, 'tBTCUSD')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
