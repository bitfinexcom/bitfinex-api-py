import os
import sys
sys.path.append('../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG'
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

def start():
  bfx.ws.subscribe('candles', 'tBTCUSD', timeframe='1m')
  bfx.ws.subscribe('trades', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
