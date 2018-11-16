import os
import sys
sys.path.append('../')

from bfxapi.websockets.LiveWebsocket import LiveBfxWebsocket

'''
This script requires you to run an instance of the bfx-hf-data-server on 
port 8899. For more info on how to setup the data-server please visit:
https://github.com/bitfinexcom/bfx-hf-data-server
'''

ws = LiveBfxWebsocket(
  logLevel='INFO'
)

@ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@ws.on('new_candle')
def log_candle(candle):
  print ("New candle: {}".format(candle))

@ws.on('new_trade')
def log_trade(trade):
  print ("New trade: {}".format(trade))

def start():
  ws.subscribe('candles', 'tBTCUSD', timeframe='1m')
  ws.subscribe('trades', 'tBTCUSD')

ws.on('connected', start)
ws.run()
