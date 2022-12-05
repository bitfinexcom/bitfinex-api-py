from collections import OrderedDict

from bfxapi import Client, Constants

from bfxapi.websocket import BfxWebsocketClient
from bfxapi.websocket.enums import Channels, Errors
from bfxapi.websocket.typings import Subscriptions, TradingPairRawBooks, TradingPairRawBook

class RawOrderBook(object):
    def __init__(self, symbols: list[str]):
        self.__raw_order_book = {
            symbol: { 
                "bids": OrderedDict(), "asks": OrderedDict() 
            } for symbol in symbols
        }
            
    def update(self, symbol: str, data: TradingPairRawBook) -> None:
        order_id, price, amount = data["ORDER_ID"], data["PRICE"], data["AMOUNT"]

        kind = (amount > 0) and "bids" or "asks"

        if price > 0:
            self.__raw_order_book[symbol][kind][order_id] = { 
                "order_id": order_id,
                "price": price, 
                "amount": amount 
            }

        if price == 0:
            if order_id in self.__raw_order_book[symbol][kind]:
                del self.__raw_order_book[symbol][kind][order_id]

SYMBOLS = [ "tBTCUSD", "tLTCUSD", "tLTCBTC", "tETHUSD", "tETHBTC" ]

raw_order_book = RawOrderBook(symbols=SYMBOLS)

bfx = Client(WSS_HOST=Constants.PUB_WSS_HOST)

@bfx.wss.on("wss-error")
def on_wss_error(code: Errors, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channels.BOOK, symbol=symbol, prec="R0")

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_raw_book_snapshot")
def on_t_raw_book_snapshot(subscription: Subscriptions.Book, snapshot: TradingPairRawBooks):
    for data in snapshot:
        raw_order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_raw_book_update")
def on_t_raw_book_update(subscription: Subscriptions.Book, data: TradingPairRawBook):
    raw_order_book.update(subscription["symbol"], data)

bfx.wss.run()