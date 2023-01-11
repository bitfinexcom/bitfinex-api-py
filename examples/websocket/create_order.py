# python -c "from examples.websocket.create_order import *"

import os

from bfxapi.client import Client, Constants
from bfxapi.utils.cid import generate_unique_cid
from bfxapi.websocket.enums import Error, OrderType
from bfxapi.websocket.typings import Inputs

bfx = Client(
    WSS_HOST=Constants.WSS_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("authenticated")
async def on_open(event):
    print(f"Auth event {event}")

    order: Inputs.Order.New = {
        "gid": generate_unique_cid(),
        "type": OrderType.EXCHANGE_LIMIT,
        "symbol": "tBTCUST",
        "amount": "0.1",
        "price": "10000.0"
    }
    await bfx.wss.inputs.order_new(order)

    print(f"Order sent")

@bfx.wss.on("notification")
async def on_notification(notification):
    print(f"Notification {notification}")

@bfx.wss.on("order_new")
async def on_order_new(order_new: Inputs.Order.New):
    print(f"Order new {order_new}")

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful <{subscription}>")

bfx.wss.run()