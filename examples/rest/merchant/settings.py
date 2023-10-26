# python -c "import examples.rest.merchant.settings"

import os

from bfxapi import Client

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

if not bfx.rest.merchant.set_merchant_settings("bfx_pay_recommend_store", 1):
    print("Cannot set <bfx_pay_recommend_store> to <1>.")

print(
    "The current <bfx_pay_preferred_fiat> value is:",
    bfx.rest.merchant.get_merchant_settings("bfx_pay_preferred_fiat"),
)

settings = bfx.rest.merchant.list_merchant_settings(
    [
        "bfx_pay_dust_balance_ui",
        "bfx_pay_merchant_customer_support_url",
        "bfx_pay_merchant_underpaid_threshold",
    ]
)

for key, value in settings.items():
    print(f"<{key}>:", value)
