import os
import sys
import asyncio
import time
sys.path.append('../../../')

from bfxapi import Client, PUB_REST_HOST

bfx = Client(
  logLevel='INFO',
  rest_host=PUB_REST_HOST
)

now = int(round(time.time() * 1000))
then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago

async def get_liquidations():
  liquidations = await bfx.rest.get_liquidations(start=then, end=now)
  print(liquidations)

asyncio.get_event_loop().run_until_complete(get_liquidations())
