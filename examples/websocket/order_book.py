# python -c "from examples.websocket.order_book import *"

from collections import OrderedDict

from typing import List

from bfxapi import Client, Constants

from bfxapi.websocket.enums import Channels, Error
from bfxapi.websocket.types import Subscriptions, TradingPairBook

class OrderBook(object):
    def __init__(self, symbols: List[str]):
        self.__order_book = {
            symbol: { 
                "bids": OrderedDict(), "asks": OrderedDict() 
            } for symbol in symbols
        }
            
    def update(self, symbol: str, data: TradingPairBook) -> None:
        price, count, amount = data.PRICE, data.COUNT, data.AMOUNT

        kind = (amount > 0) and "bids" or "asks"

        if count > 0:
            self.__order_book[symbol][kind][price] = { 
                "price": price, 
                "count": count,
                "amount": amount 
            }

        if count == 0:
            if price in self.__order_book[symbol][kind]:
                del self.__order_book[symbol][kind][price]

SYMBOLS = [ "tBTCUSD", "tLTCUSD", "tLTCBTC", "tETHUSD", "tETHBTC" ]

order_book = OrderBook(symbols=SYMBOLS)

bfx = Client(WSS_HOST=Constants.PUB_WSS_HOST)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channels.BOOK, symbol=symbol)

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_book_snapshot")
def on_t_book_snapshot(subscription: Subscriptions.Book, snapshot: List[TradingPairBook]):
    for data in snapshot:
        order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_book_update")
def on_t_book_update(subscription: Subscriptions.Book, data: TradingPairBook):
    order_book.update(subscription["symbol"], data)

bfx.wss.run()