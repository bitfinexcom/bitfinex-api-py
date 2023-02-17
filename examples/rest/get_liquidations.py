# python -c "import examples.rest.get_liquidations"

import time

from bfxapi.client import Client, REST_HOST

bfx = Client(
    REST_HOST=REST_HOST
)

now = int(round(time.time() * 1000))

liquidations = bfx.rest.public.get_liquidations(start=0, end=now)
print(f"Liquidations: {liquidations}")