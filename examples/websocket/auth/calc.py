# python -c "import examples.websocket.auth.calc"

import os

from bfxapi import Client
from bfxapi.types import BaseMarginInfo, FundingInfo, SymbolMarginInfo

bfx = Client(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET"),
)


@bfx.wss.on("authenticated")
async def on_authenticated(_):
    await bfx.wss.inputs.calc("margin_base")

    await bfx.wss.inputs.calc("margin_sym_tBTCUSD")

    await bfx.wss.inputs.calc("funding_sym_fUST")


@bfx.wss.on("base_margin_info")
def on_base_margin_info(data: BaseMarginInfo):
    print("Base margin info:", data)


@bfx.wss.on("symbol_margin_info")
def on_symbol_margin_info(data: SymbolMarginInfo):
    if data.symbol == "tBTCUSD":
        print("Symbol margin info:", data)


@bfx.wss.on("funding_info_update")
def on_funding_info_update(data: FundingInfo):
    if data.symbol == "fUST":
        print("Funding info update:", data)


bfx.wss.run()
