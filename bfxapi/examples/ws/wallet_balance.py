import os
import sys
sys.path.append('../../../')
from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='INFO'
)

@bfx.ws.on('wallet_snapshot')
def log_snapshot(wallets, data):
  for wallet in wallets:
    print (wallet)
  
  # or bfx.ws.wallets.get_wallets()

@bfx.ws.on('wallet_update')
def log_update(wallet, data):
  print ("Balance updates: {}".format(wallet))

@bfx.ws.on('error')
def log_error(msg, data):
  print ("Error: {}".format(msg))

bfx.ws.run()
