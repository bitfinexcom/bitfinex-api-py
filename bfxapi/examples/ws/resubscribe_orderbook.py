import os
import sys
sys.path.append('../../../')

from bfxapi import Client, WSChannels, WSEvents

bfx = Client(
  logLevel='INFO'
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on(WSEvents.UNSUBSCRIBED)
async def on_unsubscribe(subscription):
  print ("Unsubscribed from {}".format(subscription.symbol))
  # await subscription.subscribe()

@bfx.ws.on(WSEvents.SUBSCRIBED)
async def on_subscribe(subscription):
  print ("Subscribed to {}".format(subscription.symbol))
  # await subscription.unsubscribe()
  # or
  # await bfx.ws.unsubscribe(subscription.chanId)

@bfx.ws.once(WSEvents.SUBSCRIBED)
async def on_once_subscribe(subscription):
  print ("Performig resubscribe")
  await bfx.ws.resubscribe(subscription.chan_id)


async def start():
  await bfx.ws.subscribe(WSChannels.BOOK, 'tBTCUSD')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
