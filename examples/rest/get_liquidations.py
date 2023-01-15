# python -c "from examples.rest.get_liquidations import *"

import time

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST
)

now = int(round(time.time() * 1000))

liquidations = bfx.rest.public.get_liquidations(start=0, end=now)
print(f"Liquidations: {liquidations}")