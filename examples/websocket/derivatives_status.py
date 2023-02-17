# python -c "import examples.websocket.derivatives_status"

from bfxapi import Client, PUB_WSS_HOST
from bfxapi.websocket.enums import Error, Channel
from bfxapi.websocket.types import DerivativesStatus

from bfxapi.websocket import subscriptions

bfx = Client(WSS_HOST=PUB_WSS_HOST)

@bfx.wss.on("derivatives_status_update")
def on_derivatives_status_update(subscription: subscriptions.Status, data: DerivativesStatus):
  print(f"{subscription}:", data)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.once("open")
async def open():
    await bfx.wss.subscribe(Channel.STATUS, key="deriv:tBTCF0:USTF0")

bfx.wss.run()