import os

from bfxapi.client import Client, Constants
from bfxapi.utils.flags import calculate_offer_flags
from bfxapi.rest.typings import List, FundingOffer, Notification

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

notification: Notification = bfx.rest.auth.submit_funding_offer(
    type="LIMIT", 
    symbol="fUSD", 
    amount="123.45", 
    rate="0.001", 
    period=2, 
    flags=calculate_offer_flags(hidden=True)
)

print("Offer notification:", notification)

offers: List[FundingOffer] = bfx.rest.auth.get_active_funding_offers()

print("Offers:", offers)