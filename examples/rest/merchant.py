# python -c "import examples.rest.merchant"

import os

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

customer_info = {
    "nationality": "GB",
    "resid_country": "DE",
    "resid_city": "Berlin",
    "resid_zip_code": 1,
    "resid_street": "Timechain",
    "full_name": "Satoshi",
    "email": "satoshi3@bitfinex.com"
}

print(bfx.rest.auth.submit_invoice(
    amount=1,
    currency="USD",
    duration=864000,
    order_id="order123",
    customer_info=customer_info,
    pay_currencies=["ETH"]
))

print(bfx.rest.auth.get_invoices())

print(bfx.rest.auth.get_invoice_count_stats(status="CREATED", format="Y"))