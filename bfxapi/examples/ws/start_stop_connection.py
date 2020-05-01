import os
import sys
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG',
)

@bfx.ws.on('order_book_snapshot')
async def log_snapshot(data):
  print ("Snapshot: {}".format(data))
  # stop the websocket once a snapshot is received
  await bfx.ws.stop()

async def start():
  await bfx.ws.subscribe('book', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
