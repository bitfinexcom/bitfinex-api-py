# python -c "import examples.rest.auth.claim_position"

import os

from bfxapi import Client
from bfxapi.types import Notification, PositionClaim

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Claims all active positions
for position in bfx.rest.auth.get_positions():
    notification: Notification[PositionClaim] = bfx.rest.auth.claim_position(
        position.position_id
    )
    claim: PositionClaim = notification.data
    print(f"Position: {position} | PositionClaim: {claim}")
