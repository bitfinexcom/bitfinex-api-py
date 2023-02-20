# python -c "import examples.rest.authenticated.claim_position"

import os

from bfxapi import Client, REST_HOST

from bfxapi.rest.types import Notification, PositionClaim

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

# Claims all active positions
for position in bfx.rest.auth.get_positions():
    notification: Notification[PositionClaim] = bfx.rest.auth.claim_position(position.position_id)
    claim: PositionClaim = notification.data
    print(f"Position: {position} | PositionClaim: {claim}")