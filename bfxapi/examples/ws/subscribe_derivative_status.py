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

@bfx.ws.on('status_update')
def log_msg(msg):
  print (msg)

async def start():
  await bfx.ws.subscribe_derivative_status('tBTCF0:USTF0')

bfx.ws.on('connected', start)
bfx.ws.run()
