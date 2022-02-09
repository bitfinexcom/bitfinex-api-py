import os
import sys
sys.path.append('../../../')

from bfxapi import Client, WSEvents

bfx = Client(
  logLevel='INFO'
)

@bfx.ws.on(WSEvents.ERROR)
def log_error(err):
  print ("Error: {}".format(err))

@bfx.ws.on(WSEvents.STATUS_UPDATE)
def log_msg(msg):
  print (msg)

async def start():
  await bfx.ws.subscribe_derivative_status('tBTCF0:USTF0')

bfx.ws.on(WSEvents.CONNECTED, start)
bfx.ws.run()
