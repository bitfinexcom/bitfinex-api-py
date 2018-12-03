import os
import sys
import asyncio
sys.path.append('../')

from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY='zxXi3z6eMnRuW2mjvJSlJ08aqlHDCZbcKlqXWnzdXtF',
  API_SECRET='WL6hp6eVboiTW0dYfvIpTrX8HFPioumBoJ1w1FbAEgF',
  logLevel='DEBUG',
  rest_host='https://test.bitfinex.com/v2'
)

async def log_wallets():
  wallets = await bfx.rest.get_wallets()
  print (wallets)

t = asyncio.ensure_future(log_wallets())
asyncio.get_event_loop().run_until_complete(t)
