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

@bfx.ws.on('new_ticker')
def log_candle(ticker):
  print ("New ticker: {}".format(ticker))

async def start():
  await bfx.ws.subscribe('ticker', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
