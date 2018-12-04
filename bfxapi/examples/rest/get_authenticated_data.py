import os
import sys
import asyncio
import time
sys.path.append('../')

from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG',
  rest_host='https://test.bitfinex.com/v2'
)

async def log_wallets():
  wallets = await bfx.rest.get_wallets()
  print ("Wallets:")
  [ print (w) for w in wallets ]

async def log_active_orders():
  orders = await bfx.rest.get_active_orders('tBTCUSD')
  print ("Orders:")
  [ print (o) for o in orders ]

async def log_orders_history():
  now = int(round(time.time() * 1000))
  then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

  orders = await bfx.rest.get_order_history('tBTCUSD', 0, then)
  print ("Orders:")
  [ print (o) for o in orders ]

async def log_active_positions():
  positions = await bfx.rest.get_active_position()
  print ("Positions:")
  [ print (p) for p in positions ]

async def log_trades():
  now = int(round(time.time() * 1000))
  then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

  trades = await bfx.rest.get_trades('tBTCUSD', 0, then)
  print ("Trades")
  [ print (t) for t in trades]

async def run():
  await log_wallets()
  await log_active_orders()
  await log_orders_history()
  await log_active_positions()
  await log_trades()
  

t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
