import os
import sys
from tkinter import E
sys.path.append('../../../')

from bfxapi import Client, Order, WSEvents

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

@bfx.ws.on(WSEvents.ORDER_CLOSED)
def order_cancelled(order):
  print ("Order cancelled.")
  print (order)

@bfx.ws.on(WSEvents.ORDER_CONFIRMED)
async def trade_completed(order):
  print ("Order confirmed.")
  print (order)
  await bfx.ws.cancel_order(order.id)

@bfx.ws.on(WSEvents.ERROR)
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.once(WSEvents.AUTHENTICATED)
async def submit_order(auth_message):
  # create an initial order at a really low price so it stays open
  await bfx.ws.submit_order('tBTCUSD', 10, 1, Order.Type.EXCHANGE_LIMIT)

bfx.ws.run()
