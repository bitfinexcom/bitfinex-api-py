# python -c "import examples.rest.authenticated.toggle_keep_funding"

import os

from bfxapi import Client, REST_HOST

from bfxapi.rest.types import List, FundingLoan, Notification

bfx = Client(
    rest_host=REST_HOST,
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

loans: List[FundingLoan] = bfx.rest.auth.get_funding_loans(symbol="fUSD")

# Set every loan's keep funding status to <off> (1: <on>, 2: <off>)
notification: Notification[None] = bfx.rest.auth.toggle_keep_funding(
    type="loan",
    ids=[ loan.id for loan in loans ],
    changes={ loan.id: 2 for loan in loans }
)

print("Toggle keep funding notification:", notification)
