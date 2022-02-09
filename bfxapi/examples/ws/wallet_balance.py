import os
import sys
sys.path.append('../../../')
from bfxapi import Client, WSEvents

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='INFO'
)

@bfx.ws.on(WSEvents.WALLET_SNAPSHOT)
def log_snapshot(wallets):
  for wallet in wallets:
    print (wallet)
  
  # or bfx.ws.wallets.get_wallets()

@bfx.ws.on(WSEvents.WALLET_UPDATE)
def log_update(wallet):
  print ("Balance updates: {}".format(wallet))

@bfx.ws.on(WSEvents.ERROR)
def log_error(msg):
  print ("Error: {}".format(msg))

bfx.ws.run()
