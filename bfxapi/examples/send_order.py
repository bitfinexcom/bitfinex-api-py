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

@ws.on('order_closed')
def trade_completed(order, trade):
  print ("Order filled.")
  print (order)
  print (trade)

@ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@ws.on('authenticated')
async def submit_order(auth_message):
  await ws.submit_order('tBTCUSD', 0, 0.01, 'EXCHANGE MARKET')

# If you dont want to use a decorator
# ws.on('authenticated', submit_order)
# ws.on('error', log_error)

# You can also provide a callback
# await ws.submit_order('tBTCUSD', 0, 0.01,
# 'EXCHANGE MARKET', onComplete=trade_complete)

ws.run()
