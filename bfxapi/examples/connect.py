import os
import sys
sys.path.append('../')

from bfxapi.websockets.LiveWebsocket import LiveBfxWebsocket

ws = LiveBfxWebsocket(
  logLevel='INFO'
)

@ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@ws.on('all')
async def log_output(output):
  print ("WS: {}".format(output))

ws.run()
