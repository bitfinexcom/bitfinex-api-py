# python -c "import examples.rest.authenticated.submit_order"

import os

from bfxapi import Client, REST_HOST
from bfxapi.enums import OrderType, Flag
from bfxapi.rest.types import Notification, Order

bfx = Client(
    rest_host=REST_HOST,
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Submit a new order
submit_order_notification: Notification[Order] = bfx.rest.auth.submit_order(
    type=OrderType.EXCHANGE_LIMIT,
    symbol="tBTCUST", 
    amount=0.015, 
    price=10000, 
    flags=Flag.HIDDEN + Flag.OCO + Flag.CLOSE
)

print("Submit order notification:", submit_order_notification)

order: Order = submit_order_notification.data

# Update its amount and its price
update_order_notification: Notification[Order] = bfx.rest.auth.update_order(
    id=order.id,
    amount=0.020, 
    price=10150
)

print("Update order notification:", update_order_notification)

# Cancel it by its ID
cancel_order_notification: Notification[Order] = bfx.rest.auth.cancel_order(
    id=order.id
)

print("Cancel order notification:", cancel_order_notification)