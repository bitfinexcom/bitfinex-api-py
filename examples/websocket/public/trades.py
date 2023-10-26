# python -c "import examples.websocket.public.trades"

from bfxapi import Client
from bfxapi.types import Candle, TradingPairTrade
from bfxapi.websocket.subscriptions import Candles, Trades

bfx = Client()


@bfx.wss.on("candles_update")
def on_candles_update(_sub: Candles, candle: Candle):
    print(f"New candle: {candle}")


@bfx.wss.on("t_trade_execution")
def on_t_trade_execution(_sub: Trades, trade: TradingPairTrade):
    print(f"New trade: {trade}")


@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe("candles", key="trade:1m:tBTCUSD")

    await bfx.wss.subscribe("trades", symbol="tBTCUSD")


bfx.wss.run()
