# python -c "import examples.rest.get_positions_history"

import os
import time

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

now = int(round(time.time() * 1000))

positions_history = bfx.rest.auth.get_position_history(end=now, limit=50)
print(positions_history)
