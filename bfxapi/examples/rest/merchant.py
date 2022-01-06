import os
import sys
import asyncio
sys.path.append('../../../')
from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

async def run():
  await bfx.rest.submit_invoice(amount='2.0', currency='USD', pay_currencies=['BTC', 'ETH'], order_id='order123', webhook='https://example.com/api/v3/order/order123',
                                           redirect_url='https://example.com/api/v3/order/order123', customer_info_nationality='DE',
                                           customer_info_resid_country='GB', customer_info_resid_city='London', customer_info_resid_zip_code='WC2H 7NA',
                                           customer_info_resid_street='5-6 Leicester Square', customer_info_resid_building_no='23 A',
                                           customer_info_full_name='John Doe', customer_info_email='john@example.com', duration=86339)

  invoices = await bfx.rest.get_invoices()
  print(invoices)

  # await bfx.rest.complete_invoice(id=invoices[0]['id'], pay_ccy='BTC', deposit_id=1357996)

  unlinked_deposits = await bfx.rest.get_unlinked_deposits(ccy='BTC')
  print(unlinked_deposits)


t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
