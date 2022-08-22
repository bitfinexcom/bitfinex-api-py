import os
import sys
import asyncio
sys.path.append('../../../')

from bfxapi import Client, WS_HOST, REST_HOST

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

# Create funding requires private hosts
bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG',
  ws_host=WS_HOST,
  rest_host=REST_HOST
)

async def create_funding():
  response = await bfx.rest.submit_funding_offer("fUSD", 1000, 0.012, 7)
  # response is in the form of a Notification object
  # notify_info is in the form of a FundingOffer
  print ("Offer: ", response.notify_info)

async def cancel_funding():
  response = await bfx.rest.submit_cancel_funding_offer(41235958)
  # response is in the form of a Notification object
  # notify_info is in the form of a FundingOffer
  print ("Offer: ", response.notify_info)

async def run():
  await create_funding()
  await cancel_funding()

t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
