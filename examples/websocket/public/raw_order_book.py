# python -c "import examples.websocket.public.raw_order_book"

from collections import OrderedDict

from typing import List, Dict

import zlib

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import TradingPairRawBook
from bfxapi.websocket.subscriptions import Book
from bfxapi.websocket.enums import Channel, Error

class RawOrderBook:
    def __init__(self, symbols: List[str]):
        self.__raw_order_book = {
            symbol: {
                "bids": OrderedDict(), "asks": OrderedDict() 
            } for symbol in symbols
        }

        self.cooldown: Dict[str, bool] = \
            { symbol: False for symbol in symbols }

    def update(self, symbol: str, data: TradingPairRawBook) -> None:
        order_id, price, amount = data.order_id, data.price, data.amount

        kind = "bids" if amount > 0 else "asks"

        if price > 0:
            self.__raw_order_book[symbol][kind][order_id] = {
                "order_id": order_id,
                "price": price, 
                "amount": amount 
            }

        if price == 0:
            if order_id in self.__raw_order_book[symbol][kind]:
                del self.__raw_order_book[symbol][kind][order_id]

    def verify(self, symbol: str, checksum: int) -> bool:
        values: List[int] = [ ]

        bids = sorted([ (data["order_id"], data["price"], data["amount"]) \
            for _, data in self.__raw_order_book[symbol]["bids"].items() ],
                key=lambda data: (-data[1], data[0]))

        asks = sorted([ (data["order_id"], data["price"], data["amount"]) \
            for _, data in self.__raw_order_book[symbol]["asks"].items() ],
                key=lambda data: (data[1], data[0]))

        if len(bids) < 25 or len(asks) < 25:
            raise AssertionError("Not enough bids or asks (need at least 25).")

        for _i in range(25):
            bid, ask = bids[_i], asks[_i]
            values.extend([ bid[0], bid[2] ])
            values.extend([ ask[0], ask[2] ])

        local = ":".join(str(value) for value in values)

        crc32 = zlib.crc32(local.encode("UTF-8"))

        return crc32 == checksum

SYMBOLS = [ "tLTCBTC", "tETHUSD", "tETHBTC" ]

raw_order_book = RawOrderBook(symbols=SYMBOLS)

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channel.BOOK, symbol=symbol, prec="R0")

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_raw_book_snapshot")
def on_t_raw_book_snapshot(subscription: Book, snapshot: List[TradingPairRawBook]):
    for data in snapshot:
        raw_order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_raw_book_update")
def on_t_raw_book_update(subscription: Book, data: TradingPairRawBook):
    raw_order_book.update(subscription["symbol"], data)

@bfx.wss.on("checksum")
async def on_checksum(subscription: Book, value: int):
    symbol = subscription["symbol"]

    if raw_order_book.verify(symbol, value):
        raw_order_book.cooldown[symbol] = False
    elif not raw_order_book.cooldown[symbol]:
        print("Mismatch between local and remote checksums: "
            f"restarting book for symbol <{symbol}>...")

        await bfx.wss.resubscribe(sub_id=subscription["sub_id"])

        raw_order_book.cooldown[symbol] = True

bfx.wss.run()
