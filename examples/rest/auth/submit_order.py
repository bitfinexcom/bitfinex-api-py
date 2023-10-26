# python -c "import examples.rest.auth.submit_order"

import os

from bfxapi import Client
from bfxapi.types import Notification, Order

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Submit a new order
submit_order_notification: Notification[Order] = bfx.rest.auth.submit_order(
    type="EXCHANGE LIMIT", symbol="tBTCUST", amount=0.015, price=10000
)

print("Submit order notification:", submit_order_notification)

order: Order = submit_order_notification.data

# Update its amount and its price
update_order_notification: Notification[Order] = bfx.rest.auth.update_order(
    id=order.id, amount=0.020, price=10150
)

print("Update order notification:", update_order_notification)

# Cancel it by its ID
cancel_order_notification: Notification[Order] = bfx.rest.auth.cancel_order(id=order.id)

print("Cancel order notification:", cancel_order_notification)
