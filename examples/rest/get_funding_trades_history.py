# python -c "import examples.rest.get_funding_trades_history"

import os

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

print(bfx.rest.auth.get_funding_trades_history())