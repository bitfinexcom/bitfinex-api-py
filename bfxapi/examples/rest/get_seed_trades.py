import os
import sys
import asyncio
sys.path.append('../../../')

from bfxapi import Client, PUB_WS_HOST, PUB_REST_HOST

# Retrieving seed trades requires public hosts
bfx = Client(
  logLevel='INFO',
  ws_host=PUB_WS_HOST,
  rest_host=PUB_REST_HOST
)

async def get_seeds():
  candles = await bfx.rest.get_seed_candles('tBTCUSD')
  print (candles)

asyncio.get_event_loop().run_until_complete(get_seeds())
