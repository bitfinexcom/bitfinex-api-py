# python -c "import examples.websocket.public.derivatives_status"

from bfxapi import Client, PUB_WSS_HOST
from bfxapi.types import DerivativesStatus
from bfxapi.websocket.subscriptions import Status

from bfxapi.websocket.enums import Error, Channel

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("derivatives_status_update")
def on_derivatives_status_update(subscription: Status, data: DerivativesStatus):
    print(f"{subscription}:", data)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe(Channel.STATUS, key="deriv:tBTCF0:USTF0")

bfx.wss.run()
