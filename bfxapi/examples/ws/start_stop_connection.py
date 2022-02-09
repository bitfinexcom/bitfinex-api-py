import os
import sys
sys.path.append('../../../')

from bfxapi import Client, WSEvents, WSChannels

bfx = Client(
  logLevel='DEBUG',
)

@bfx.ws.on(WSEvents.ORDER_BOOK_SNAPSHOT)
async def log_snapshot(data):
  print ("Snapshot: {}".format(data))
  # stop the websocket once a snapshot is received
  await bfx.ws.stop()

async def start():
  await bfx.ws.subscribe(WSChannels.BOOK, 'tBTCUSD')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
