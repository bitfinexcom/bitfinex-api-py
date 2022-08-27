import os
import sys
sys.path.append('../../../')

from bfxapi import Client
from bfxapi.constants import WS_HOST, REST_HOST

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG',
  ws_host=WS_HOST,
  rest_host=REST_HOST,
  dead_man_switch=True, # <-- kill all orders if this connection drops
  channel_filter=['wallet'] # <-- only receive wallet updates
)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on('authenticated')
async def submit_order(auth_message):
  print ("Authenticated!!")
