import os
import sys
sys.path.append('../../../')

from bfxapi import Client, Order, WSEvents

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

@bfx.ws.on(WSEvents.ORDER_SNAPSHOT)
async def cancel_all(data):
  await bfx.ws.cancel_all_orders()

@bfx.ws.on(WSEvents.ORDER_CONFIRMED)
async def trade_completed(order):
  print ("Order confirmed.")
  print (order)
  ## close the order
  # await order.close()
  # or
  # await bfx.ws.cancel_order(order.id)
  # or
  # await bfx.ws.cancel_all_orders()

@bfx.ws.on(WSEvents.ERROR)
def log_error(msg):
  print ("Error: {}".format(msg))

@bfx.ws.on(WSEvents.AUTHENTICATED)
async def submit_order(auth_message):
  await bfx.ws.submit_order(symbol='tBTCUSD', price=None, amount=0.01, market_type=Order.Type.EXCHANGE_MARKET)

# If you dont want to use a decorator
# ws.on(WSEvents.AUTHENTICATED, submit_order)
# ws.on(WSEvents.ERROR, log_error)

# You can also provide a callback
# await ws.submit_order('tBTCUSD', 0, 0.01,
# 'EXCHANGE MARKET', onClose=trade_complete)

bfx.ws.run()
