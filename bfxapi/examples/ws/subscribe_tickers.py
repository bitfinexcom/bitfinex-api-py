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

@bfx.ws.on(WSEvents.NEW_FUNDING_TICKER)
def log_ticker(ticker):
  print ("New ticker: {}".format(ticker))

async def start():
  await bfx.ws.subscribe(WSChannels.TICKER, 'fUSD')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
