# python -c "import examples.rest.authenticated.submit_funding_offer"

import os

from bfxapi import Client, REST_HOST
from bfxapi.enums import FundingOfferType, Flag
from bfxapi.rest.types import Notification, FundingOffer

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
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