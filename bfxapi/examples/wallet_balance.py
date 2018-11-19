import os
import sys
sys.path.append('../')

from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='INFO'
)

@bfx.ws.on('wallet_snapshot')
def log_snapshot(data):
  print ("Opening balance: {}".format(data))

@bfx.ws.on('wallet_update')
def log_update(data):
  print ("Balance updates: {}".format(data))

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

bfx.ws.run()
