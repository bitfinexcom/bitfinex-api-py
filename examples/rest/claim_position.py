# python -c "from examples.rest.claim_position import *"

import os

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

open_margin_positions = bfx.rest.auth.get_positions()

# claim all positions
for position in open_margin_positions:
    print(f"Position {position}")
    claim = bfx.rest.auth.claim_position(position.POSITION_ID, amount=0.000001)
    print(f"Claim {claim.NOTIFY_INFO}")