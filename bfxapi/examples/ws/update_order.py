import os
import sys
sys.path.append('../')

from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

@bfx.ws.on('order_update')
def order_updated(order, trade):
  print ("Order updated.")
  print (order)
  print (trade)

@bfx.ws.once('order_update')
async def order_once_updated(order, trade):
  # update a second time using the object function
  await order.update(price=80, amount=0.02, flags="2nd update")

@bfx.ws.once('order_confirmed')
async def trade_completed(order, trade):
  print ("Order confirmed.")
  print (order)
  print (trade)
  await bfx.ws.update_order(order.id, price=100, amount=0.01)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.once('authenticated')
async def submit_order(auth_message):
  # create an inital order a really low price so it stays open
  await bfx.ws.submit_order('tBTCUSD', 10, 1, 'EXCHANGE LIMIT')

bfx.ws.run()
