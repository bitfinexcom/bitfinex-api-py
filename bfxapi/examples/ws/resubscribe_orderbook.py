import os
import sys
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='INFO'
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('unsubscribed')
async def on_unsubscribe(subscription, data):
  print ("Unsubscribed from {}".format(subscription.symbol))
  # await subscription.subscribe()

@bfx.ws.on('subscribed')
async def on_subscribe(subscription, data):
  print ("Subscribed to {}".format(subscription.symbol))
  # await subscription.unsubscribe()
  # or
  # await bfx.ws.unsubscribe(subscription.chanId)

@bfx.ws.once('subscribed')
async def on_once_subscribe(subscription, data):
  print ("Performig resubscribe")
  await bfx.ws.resubscribe(subscription.chan_id)


async def start():
  await bfx.ws.subscribe('book', 'tBTCUSD')

bfx.ws.on('connected', start)
bfx.ws.run()
