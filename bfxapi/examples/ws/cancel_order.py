import os
import sys
sys.path.append('../../../')

from bfxapi import Client, Order

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

@bfx.ws.on('order_closed')
def order_cancelled(order):
  print ("Order cancelled.")
  print (order)

@bfx.ws.on('order_confirmed')
async def trade_completed(order):
  print ("Order confirmed.")
  print (order)
  await bfx.ws.cancel_order(order.id)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.once('authenticated')
async def submit_order(auth_message):
  # create an initial order at a really low price so it stays open
  await bfx.ws.submit_order('tBTCUSD', 10, 1, Order.Type.EXCHANGE_LIMIT)

bfx.ws.run()
