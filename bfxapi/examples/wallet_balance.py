import os
import sys
sys.path.append('../')

from bfxapi.websockets.LiveWebsocket import LiveBfxWebsocket

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

ws = LiveBfxWebsocket(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='INFO'
)

@ws.on('wallet_snapshot')
def log_snapshot(data):
  print ("Opening balance: {}".format(data))

@ws.on('wallet_update')
def log_update(data):
  print ("Balance updates: {}".format(data))

ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

ws.run()
