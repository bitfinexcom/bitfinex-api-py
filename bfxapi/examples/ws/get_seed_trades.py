import os
import sys
import asyncio
sys.path.append('../')

from bfxapi import Client

bfx = Client(
  logLevel='INFO'
)

async def get_seeds():
  candles = await bfx.rest.get_seed_candles('tBTCUSD')
  print (candles)

asyncio.get_event_loop().run_until_complete(get_seeds())
