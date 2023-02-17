# python -c "import examples.websocket.ticker"

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.websocket import subscriptions
from bfxapi.websocket.enums import Channel
from bfxapi.websocket.types import TradingPairTicker

bfx = Client(WSS_HOST=PUB_WSS_HOST)

@bfx.wss.on("t_ticker_update")
def on_t_ticker_update(subscription: subscriptions.Ticker, data: TradingPairTicker):
    print(f"Subscription with subId: {subscription['subId']}")

    print(f"Data: {data}")

@bfx.wss.once("open")
async def open():
    await bfx.wss.subscribe(Channel.TICKER, symbol="tBTCUSD")

bfx.wss.run()