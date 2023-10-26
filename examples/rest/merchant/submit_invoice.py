# python -c "import examples.rest.merchant.submit_invoice"

import os

from bfxapi import Client
from bfxapi.types import InvoiceSubmission

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

customer_info = {
    "nationality": "DE",
    "residCountry": "GB",
    "residCity": "London",
    "residZipCode": "WC2H 7NA",
    "residStreet": "5-6 Leicester Square",
    "residBuildingNo": "23 A",
    "fullName": "John Doe",
    "email": "john@example.com",
}

invoice: InvoiceSubmission = bfx.rest.merchant.submit_invoice(
    amount=1.0,
    currency="USD",
    order_id="test",
    customer_info=customer_info,
    pay_currencies=["ETH"],
    duration=86400,
)

print("Invoice submission:", invoice)

print(
    bfx.rest.merchant.complete_invoice(id=invoice.id, pay_currency="ETH", deposit_id=1)
)

print(bfx.rest.merchant.get_invoices(limit=25))

print(
    bfx.rest.merchant.get_invoices_paginated(
        page=1, page_size=60, sort="asc", sort_field="t"
    )
)
