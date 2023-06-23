# python -c "import examples.websocket.public.trades"

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import Candle, TradingPairTrade
from bfxapi.websocket.subscriptions import Candles, Trades
from bfxapi.websocket.enums import Error, Channel

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("candles_update")
def on_candles_update(_sub: Candles, candle: Candle):
    print(f"New candle: {candle}")

@bfx.wss.on("t_trade_execution")
def on_t_trade_execution(_sub: Trades, trade: TradingPairTrade):
    print(f"New trade: {trade}")

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe(Channel.CANDLES, key="trade:1m:tBTCUSD")

    await bfx.wss.subscribe(Channel.TRADES, symbol="tBTCUSD")

bfx.wss.run()
