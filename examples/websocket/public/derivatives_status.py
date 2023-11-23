# python -c "import examples.websocket.public.derivatives_status"

from bfxapi import Client
from bfxapi.types import DerivativesStatus
from bfxapi.websocket.subscriptions import Status

bfx = Client()


@bfx.wss.on("derivatives_status_update")
def on_derivatives_status_update(subscription: Status, data: DerivativesStatus):
    print(f"{subscription}:", data)


@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe("status", key="deriv:tBTCF0:USTF0")


bfx.wss.run()
