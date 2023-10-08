# python -c "import examples.websocket.public.ticker"

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import TradingPairTicker
from bfxapi.websocket.subscriptions import Ticker
from bfxapi.websocket.enums import Channel

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("t_ticker_update")
def on_t_ticker_update(subscription: Ticker, data: TradingPairTicker):
    print(f"Subscription with sub_id: {subscription['sub_id']}")

    print(f"Data: {data}")

@bfx.wss.on("open")
async def on_open():
    await bfx.wss.subscribe(Channel.TICKER, symbol="tBTCUSD")

bfx.wss.run()
