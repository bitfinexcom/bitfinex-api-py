import sys
sys.path.append('../../../')

from bfxapi import Client
from bfxapi.constants import PUB_WS_HOST, PUB_REST_HOST

# Retrieving derivative status requires public hosts
bfx = Client(
  logLevel='DEBUG',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

@bfx.ws.on('error')
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on('status_update')
def log_msg(msg):
  print (msg)

async def start():
  await bfx.ws.subscribe_derivative_status('tBTCF0:USTF0')

bfx.ws.on('connected', start)
bfx.ws.run()
