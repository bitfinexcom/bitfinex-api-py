# python -c "import examples.rest.merchant.submit_invoice"

import os

from bfxapi import Client, REST_HOST 

from bfxapi.rest.types import InvoiceSubmission

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

customer_info = {
    "nationality": "DE",
    "residCountry": "GB",
    "residCity": "London",
    "residZipCode": "WC2H 7NA",
    "residStreet": "5-6 Leicester Square",
    "residBuildingNo": "23 A",
    "fullName": "John Doe",
    "email": "john@example.com"
}

invoice: InvoiceSubmission = bfx.rest.merchant.submit_invoice(
    amount=1.0,
    currency="USD",
    order_id="test",
    customer_info=customer_info,
    pay_currencies=["ETH"],
    duration=86400 * 10
)

print("Invoice submission:", invoice)

print(bfx.rest.merchant.complete_invoice(
    id=invoice.id,
    pay_currency="ETH",
    deposit_id=1
))

print(bfx.rest.merchant.get_invoices(limit=25))