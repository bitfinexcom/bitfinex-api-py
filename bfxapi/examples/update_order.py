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

@ws.on('order_update')
def order_updated(order, trade):
  print ("Order updated.")
  print (order)
  print (trade)

@ws.once('order_confirmed')
async def trade_completed(order, trade):
  print ("Order confirmed.")
  print (order)
  print (trade)
  await ws.update_order(order.id, price=100, amount=0.01)

@ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@ws.once('authenticated')
async def submit_order(auth_message):
  # create an inital order a really low price so it stays open
  await ws.submit_order('tBTCUSD', 10, 1, 'EXCHANGE LIMIT')

ws.run()
