# python -c "from examples.websocket.ticker import *"

from bfxapi import Client, Constants

from bfxapi.websocket import subscriptions
from bfxapi.websocket.enums import Channels
from bfxapi.websocket.types import TradingPairTicker

bfx = Client(WSS_HOST=Constants.PUB_WSS_HOST)

@bfx.wss.on("t_ticker_update")
def on_t_ticker_update(subscription: subscriptions.Ticker, data: TradingPairTicker):
    print(f"Subscription with channel ID: {subscription['chanId']}")

    print(f"Data: {data}")

@bfx.wss.once("open")
async def open():
    await bfx.wss.subscribe(Channels.TICKER, symbol="tBTCUSD")

bfx.wss.run()