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

@bfx.ws.on('new_funding_ticker')
def log_ticker(ticker):
  print ("New ticker: {}".format(ticker))

async def start():
  await bfx.ws.subscribe('ticker', 'fUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
