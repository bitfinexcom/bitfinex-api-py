# python -c "import examples.rest.keep_taken_funding"

import os

from bfxapi.client import Client, REST_HOST

bfx = Client(
    REST_HOST=REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

loans = bfx.rest.auth.get_funding_loans(symbol="fUSD")

for loan in loans:
    print(f"Loan {loan}")

    notification = bfx.rest.auth.toggle_keep(
        funding_type="loan",
        ids=[loan.id],
        changes={
            loan.id: 2  # (1 if true, 2 if false)
        }
    )

    print("Funding keep notification:", notification)