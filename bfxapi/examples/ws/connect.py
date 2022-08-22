import os
import sys
sys.path.append('../../../')

from bfxapi import Client, PUB_WS_HOST, PUB_REST_HOST

bfx = Client(
  logLevel='DEBUG',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on('all')
async def log_output(output):
  print ("WS: {}".format(output))

bfx.ws.run()
