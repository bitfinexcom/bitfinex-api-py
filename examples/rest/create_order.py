# python -c "import examples.rest.create_order"

import os
from bfxapi.client import Client, Constants
from bfxapi.enums import OrderType, Flag

bfx = Client(
    REST_HOST=Constants.REST_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

# Create a new order
submitted_order = bfx.rest.auth.submit_order(
    type=OrderType.EXCHANGE_LIMIT,
    symbol="tBTCUST", 
    amount="0.015", 
    price="10000", 
    flags=Flag.HIDDEN + Flag.OCO + Flag.CLOSE
)

print("Submit Order Notification:", submitted_order)

# Update it
updated_order = bfx.rest.auth.update_order(
    id=submitted_order.notify_info.id,
    amount="0.020", 
    price="10100"
)

print("Update Order Notification:", updated_order)

# Delete it
canceled_order = bfx.rest.auth.cancel_order(id=submitted_order.notify_info.id)

print("Cancel Order Notification:", canceled_order)
