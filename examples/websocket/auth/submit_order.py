# python -c "import examples.websocket.auth.submit_order"

import os

from bfxapi import Client
from bfxapi.types import Notification, Order

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET"),
)


@bfx.wss.on("authenticated")
async def on_authenticated(event):
    print(f"Authentication: {event}")

    await bfx.wss.inputs.submit_order(
        type="EXCHANGE LIMIT", symbol="tBTCUSD", amount=0.165212, price=30264.0
    )

    print("The order has been sent.")


@bfx.wss.on("on-req-notification")
async def on_notification(notification: Notification[Order]):
    print(f"Notification: {notification}.")


@bfx.wss.on("order_new")
async def on_order_new(order_new: Order):
    print(f"Order new: {order_new}")


@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for <{subscription}>.")


bfx.wss.run()
