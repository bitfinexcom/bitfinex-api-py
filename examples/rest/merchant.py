# python -c "import examples.rest.merchant"

import os

from bfxapi.client import Client, Constants
from bfxapi.rest.types import CustomerInfo

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

customer_info: CustomerInfo = CustomerInfo(
    nationality="GB",
    resid_country="DE",
    resid_city="Berlin",
    resid_zip_code=1,
    resid_street="Timechain",
    full_name="Satoshi",
    email="satoshi3@bitfinex.com",
    tos_accepted=None,
    resid_building_no=None
)

print(bfx.rest.auth.submit_invoice(
    amount=1,
    currency="USD",
    duration=864000,
    order_id="order123",
    customer_info=customer_info,
    pay_currencies=["ETH"],
))