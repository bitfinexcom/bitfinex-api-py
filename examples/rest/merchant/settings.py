# python -c "import examples.rest.merchant.settings"

import os

from bfxapi import Client, REST_HOST 

from bfxapi.rest.enums import MerchantSettingsKey

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

if not bfx.rest.merchant.set_merchant_settings(MerchantSettingsKey.RECOMMEND_STORE, 1):
    print(f"Cannot set <{MerchantSettingsKey.RECOMMEND_STORE}> to <1>.")

print(f"The current <{MerchantSettingsKey.PREFERRED_FIAT}> value is:", 
    bfx.rest.merchant.get_merchant_settings(MerchantSettingsKey.PREFERRED_FIAT))

settings = bfx.rest.merchant.list_merchant_settings([
    MerchantSettingsKey.DUST_BALANCE_UI,
    MerchantSettingsKey.MERCHANT_CUSTOMER_SUPPORT_URL,
    MerchantSettingsKey.MERCHANT_UNDERPAID_THRESHOLD
])

for key, value in settings.items():
    print(f"<{key}>:", value)