import os
import sys
sys.path.append('../')

from bfxapi import Client

bfx = Client(
  logLevel='DEBUG'
)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on('all')
async def log_output(output):
  print ("WS: {}".format(output))

bfx.ws.run()
