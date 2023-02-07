# python -c "import examples.rest.create_funding_offer"

import os

from bfxapi.client import Client, Constants
from bfxapi.enums import FundingOfferType, Flag

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

notification = bfx.rest.auth.submit_funding_offer(
    type=FundingOfferType.LIMIT, 
    symbol="fUSD", 
    amount="123.45", 
    rate="0.001", 
    period=2, 
    flags=Flag.HIDDEN
)

print("Offer notification:", notification)

offers = bfx.rest.auth.get_funding_offers(symbol="fUSD")

print("Offers:", offers)

# Cancel all funding offers
notification = bfx.rest.auth.cancel_all_funding_offers(currency="fUSD")

print(notification)