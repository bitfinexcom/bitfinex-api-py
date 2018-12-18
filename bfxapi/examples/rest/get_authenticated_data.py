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

now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

async def log_wallets():
  wallets = await bfx.rest.get_wallets()
  print ("Wallets:")
  [ print (w) for w in wallets ]

async def log_active_orders():
  orders = await bfx.rest.get_active_orders('tBTCUSD')
  print ("Orders:")
  [ print (o) for o in orders ]

async def log_orders_history():
  orders = await bfx.rest.get_order_history('tBTCUSD', 0, then)
  print ("Orders:")
  [ print (o) for o in orders ]

async def log_active_positions():
  positions = await bfx.rest.get_active_positions()
  print ("Positions:")
  [ print (p) for p in positions ]

async def log_trades():
  trades = await bfx.rest.get_trades('tBTCUSD', 0, then)
  print ("Trades:")
  [ print (t) for t in trades]

async def log_order_trades():
  order_id = 1151353463
  trades = await bfx.rest.get_order_trades('tBTCUSD', order_id)
  print ("Trade orders:")
  [ print (t) for t in trades]

async def log_funding_offers():
  offers = await bfx.rest.get_funding_offers('tBTCUSD')
  print ("Offers:")
  [ print (o) for o in offers]

async def log_funding_offer_history():
  offers = await bfx.rest.get_funding_offer_history('tBTCUSD', 0, then)
  print ("Offers history:")
  [ print (o) for o in offers]

async def log_funding_loans():
  loans = await bfx.rest.get_funding_loans('tBTCUSD')
  print ("Funding loans:")
  [ print (l) for l in loans ]

async def log_funding_loans_history():
  loans = await bfx.rest.get_funding_loan_history('tBTCUSD', 0, then)
  print ("Funding loan history:")
  [ print (l) for l in loans ]

async def log_funding_credits():
  credits = await bfx.rest.get_funding_credits('tBTCUSD')
  print ("Funding credits:")
  [ print (c) for c in credits ]

async def log_funding_credits_history():
  credit = await bfx.rest.get_funding_credit_history('tBTCUSD', 0, then)
  print ("Funding credit history:")
  [ print (c) for c in credit ]

async def run():
  await log_wallets()
  await log_active_orders()
  await log_orders_history()
  await log_active_positions()
  await log_trades()
  await log_order_trades()
  await log_funding_offers()
  await log_funding_offer_history()
  await log_funding_credits()
  await log_funding_credits_history()
  

t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
