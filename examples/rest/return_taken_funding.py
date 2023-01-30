# python -c "import examples.rest.return_taken_funding"

import os

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

loans = bfx.rest.auth.get_funding_loans(symbol="fUSD")

for loan in loans:
    print(f"Loan {loan}")

    notification = bfx.rest.auth.submit_funding_close(
        id=loan.id
    )

    print("Funding close notification:", notification)