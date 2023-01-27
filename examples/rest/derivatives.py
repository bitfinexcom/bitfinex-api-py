# python -c "import examples.rest.derivatives"

import os

from bfxapi.client import Client, Constants

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

# Create a new order
submitted_order = bfx.rest.auth.submit_order(
    symbol="tBTCF0:USTF0",
    amount="0.015",
    price="16700",
    lev=10,
    type="LIMIT"
)

print("Submit Order Notification:", submitted_order)

# Get position collateral limits
limits = bfx.rest.auth.get_derivative_position_collateral_limits(symbol="tBTCF0:USTF0")
print(f"Limits {limits}")

# Update position collateral
response = bfx.rest.auth.set_derivative_position_collateral(symbol="tBTCF0:USTF0", collateral=50)
print(response.status)

