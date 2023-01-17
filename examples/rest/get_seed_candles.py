# python -c "from examples.rest.get_seed_candles import *"

import time

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST
)

print(f"Candles: {bfx.rest.public.get_seed_candles(symbol='tBTCUSD')}")

# Be sure to specify a period or aggregated period when retrieving funding candles.
# If you wish to mimic the candles found in the UI, use the following setup to aggregate all funding candles: a30:p2:p30
print(f"Candles: {bfx.rest.public.get_seed_candles(symbol='fUSD:a30:p2:p30', tf='15m')}")