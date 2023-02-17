# python -c "import examples.rest.merchant"

import os

from bfxapi.client import Client, REST_HOST 

bfx = Client(
    REST_HOST=REST_HOST,
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

invoice = bfx.rest.merchant.submit_invoice(
    amount=1,
    currency="USD",
    duration=864000,
    order_id="order123",
    customer_info=customer_info,
    pay_currencies=["ETH"]
)

print(bfx.rest.merchant.get_invoices())

print(bfx.rest.merchant.get_invoice_count_stats(status="CREATED", format="Y"))

print(bfx.rest.merchant.get_invoice_earning_stats(currency="USD", format="Y"))

print(bfx.rest.merchant.get_currency_conversion_list())

print(bfx.rest.merchant.complete_invoice(
    id=invoice.id,
    pay_currency="ETH",
    deposit_id=1
))