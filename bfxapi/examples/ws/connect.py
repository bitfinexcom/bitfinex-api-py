import os
import sys

from bfxapi.websockets.constants import WSEvents
sys.path.append('../../../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG'
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on(WSEvents.ALL)
async def log_output(output):
  print ("WS: {}".format(output))

bfx.ws.run()
