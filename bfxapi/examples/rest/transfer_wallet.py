import os
import sys
import asyncio
import time
sys.path.append('../../../')

from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

async def transfer_wallet():
  response = await bfx.rest.submit_wallet_transfer("exchange", "margin", "BTC", "BTC", 0.1)
  # response is in the form of a Notification object
  # notify_info is in the form of a Transfer object
  print ("Transfer: ", response.notify_info)

async def deposit_address():
  response = await bfx.rest.get_wallet_deposit_address("exchange", "bitcoin")
  # response is in the form of a Notification object
  # notify_info is in the form of a DepositAddress object
  print ("Address: ", response.notify_info)

async def create_new_address():
  response = await bfx.rest.create_wallet_deposit_address("exchange", "bitcoin")
  # response is in the form of a Notification object
  # notify_info is in the form of a DepositAddress object
  print ("Address: ", response.notify_info)

async def withdraw():
  # tetheruse = Tether (ERC20)
  response = await bfx.rest.submit_wallet_withdraw("exchange", "tetheruse", 5, "0xc5bbb852f82c24327693937d4012f496cff7eddf")
  # response is in the form of a Notification object
  # notify_info is in the form of a DepositAddress object
  print ("Address: ", response.notify_info)

async def run():
  await transfer_wallet()
  await deposit_address()
  await withdraw()

t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
