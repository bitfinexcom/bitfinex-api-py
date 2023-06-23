# python -c "import examples.rest.authenticated.submit_funding_offer"

import os

from bfxapi import Client, REST_HOST
from bfxapi.types import Notification, FundingOffer
from bfxapi.enums import FundingOfferType, Flag

bfx = Client(
    rest_host=REST_HOST,
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Submit a new funding offer
notification: Notification[FundingOffer] = bfx.rest.auth.submit_funding_offer(
    type=FundingOfferType.LIMIT,
    symbol="fUSD",
    amount=123.45,
    rate=0.001,
    period=2,
    flags=Flag.HIDDEN
)

print("Funding Offer notification:", notification)

# Get all fUSD active funding offers
offers = bfx.rest.auth.get_funding_offers(symbol="fUSD")

print("Offers (fUSD):", offers)
