# python -c "import examples.rest.authenticated.set_derivatives_position_collateral"

import os

from bfxapi import Client, REST_HOST

from bfxapi.rest.types import DerivativePositionCollateral, DerivativePositionCollateralLimits

bfx = Client(
    rest_host=REST_HOST,
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

submit_order_notification = bfx.rest.auth.submit_order(
    type="LIMIT",
    symbol="tBTCF0:USTF0",
    amount="0.015",
    price="16700",
    lev=10
)

print("New Order:", submit_order_notification.data)

# Update the amount of collateral for tBTCF0:USTF0 derivative position
derivative_position_collateral: DerivativePositionCollateral = \
    bfx.rest.auth.set_derivative_position_collateral(symbol="tBTCF0:USTF0", collateral=50.0)

print("Status:", bool(derivative_position_collateral.status))

# Calculate the minimum and maximum collateral that can be assigned to tBTCF0:USTF0.
derivative_position_collateral_limits: DerivativePositionCollateralLimits = \
    bfx.rest.auth.get_derivative_position_collateral_limits(symbol="tBTCF0:USTF0")

print(f"Minimum collateral: {derivative_position_collateral_limits.min_collateral} | " \
    f"Maximum collateral: {derivative_position_collateral_limits.max_collateral}")
