import os
import sys

from bfxapi.websockets.constants import WSEvents
sys.path.append('../../../')

from bfxapi import Client, Order, WSEvents

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG',
  dead_man_switch=True, # <-- kill all orders if this connection drops
  channel_filter=['wallet'] # <-- only receive wallet updates
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on(WSEvents.AUTHENTICATED)
async def submit_order(auth_message):
  print ("Authenticated!!")
