# python -c "import examples.websocket.wallet_balance"

import os

from typing import List

from bfxapi import Client, WSS_HOST
from bfxapi.websocket.enums import Error
from bfxapi.websocket.types import Wallet

bfx = Client(
    WSS_HOST=WSS_HOST,
    API_KEY=os.getenv("BFX_API_KEY"),
    API_SECRET=os.getenv("BFX_API_SECRET")
)

@bfx.wss.on("wallet_snapshot")
def log_snapshot(wallets: List[Wallet]):
    for wallet in wallets:
        print(f"Balance: {wallet}")

@bfx.wss.on("wallet_update")
def log_update(wallet: Wallet):
    print(f"Balance update: {wallet}")

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

bfx.wss.run()