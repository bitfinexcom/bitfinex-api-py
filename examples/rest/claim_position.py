# python -c "import examples.rest.claim_position"

import os

from bfxapi.client import Client, REST_HOST

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

open_margin_positions = bfx.rest.auth.get_positions()

# claim all positions
for position in open_margin_positions:
    print(f"Position {position}")
    claim = bfx.rest.auth.claim_position(position.position_id, amount=0.000001)
    print(f"PositionClaim {claim.notify_info}")