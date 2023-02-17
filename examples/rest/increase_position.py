# python -c "import examples.rest.increase_position"

import os

from bfxapi.client import Client, REST_HOST

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

increase_info = bfx.rest.auth.get_increase_position_info(symbol="tBTCUSD", amount=0.0001)
print(increase_info)

# increase a margin position
notification = bfx.rest.auth.increase_position(symbol="tBTCUSD", amount=0.0001)
print(notification.notify_info)
