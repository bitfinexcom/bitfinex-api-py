import os
import sys
sys.path.append('../../../')

from bfxapi import Client, WSEvents, WSChannels

bfx = Client(
  logLevel='DEBUG',
  # Verifies that the local orderbook is up to date
  # with the bitfinex servers
  manageOrderBooks=True
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on(WSEvents.ORDER_BOOK_UPDATE)
def log_update(data):
  print ("Book update: {}".format(data))

@bfx.ws.on(WSEvents.ORDER_BOOK_SNAPSHOT)
def log_snapshot(data):
  print ("Initial book: {}".format(data))

async def start():
  await bfx.ws.subscribe(WSChannels.BOOK, 'tBTCUSD')
  # bfx.ws.subscribe(WSChannels.BOOK, 'tETHUSD')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
