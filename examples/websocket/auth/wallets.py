# python -c "import examples.websocket.auth.wallets"

import os
from typing import List

from bfxapi import Client
from bfxapi.types import Wallet

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET"),
    filters=["wallet"],
)


@bfx.wss.on("wallet_snapshot")
def on_wallet_snapshot(wallets: List[Wallet]):
    for wallet in wallets:
        print(f"Wallet: {wallet.wallet_type} | {wallet.currency}")
        print(f"Available balance: {wallet.available_balance}")
        print(f"Wallet trade details: {wallet.trade_details}")


@bfx.wss.on("wallet_update")
def on_wallet_update(wallet: Wallet):
    print(f"Wallet update: {wallet}")


bfx.wss.run()
