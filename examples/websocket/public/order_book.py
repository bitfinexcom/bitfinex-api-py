# python -c "import examples.websocket.public.order_book"

from collections import OrderedDict

from typing import List, Dict

import crcmod

from bfxapi import Client, PUB_WSS_HOST

from bfxapi.types import TradingPairBook
from bfxapi.websocket.subscriptions import Book
from bfxapi.websocket.enums import Channel, Error

class OrderBook:
    def __init__(self, symbols: List[str]):
        self.__order_book = {
            symbol: {
                "bids": OrderedDict(), "asks": OrderedDict()
            } for symbol in symbols
        }

        self.cooldown: Dict[str, bool] = \
            { symbol: False for symbol in symbols }

    def update(self, symbol: str, data: TradingPairBook) -> None:
        price, count, amount = data.price, data.count, data.amount

        kind = "bids" if amount > 0 else "asks"

        if count > 0:
            self.__order_book[symbol][kind][price] = {
                "price": price, 
                "count": count,
                "amount": amount 
            }

        if count == 0:
            if price in self.__order_book[symbol][kind]:
                del self.__order_book[symbol][kind][price]

    def verify(self, symbol: str, checksum: int) -> bool:
        values: List[int] = [ ]

        bids = sorted([ (data["price"], data["count"], data["amount"]) \
            for _, data in self.__order_book[symbol]["bids"].items() ],
                key=lambda data: -data[0])

        asks = sorted([ (data["price"], data["count"], data["amount"]) \
            for _, data in self.__order_book[symbol]["asks"].items() ],
                key=lambda data: data[0])

        if len(bids) < 25 or len(asks) < 25:
            raise AssertionError("Not enough bids or asks (need at least 25).")

        for _i in range(25):
            bid, ask = bids[_i], asks[_i]
            values.extend([ bid[0], bid[2] ])
            values.extend([ ask[0], ask[2] ])

        local = ":".join(str(value) for value in values).encode("UTF-8")

        crc32 = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, xorOut=0xFFFFFFFF)

        return crc32(local) == checksum

SYMBOLS = [ "tBTCUSD", "tLTCUSD", "tLTCBTC", "tETHUSD", "tETHBTC" ]

order_book = OrderBook(symbols=SYMBOLS)

bfx = Client(wss_host=PUB_WSS_HOST)

@bfx.wss.on("wss-error")
def on_wss_error(code: Error, msg: str):
    print(code, msg)

@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe(Channel.BOOK, symbol=symbol)

@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for pair <{subscription['pair']}>")

@bfx.wss.on("t_book_snapshot")
def on_t_book_snapshot(subscription: Book, snapshot: List[TradingPairBook]):
    for data in snapshot:
        order_book.update(subscription["symbol"], data)

@bfx.wss.on("t_book_update")
def on_t_book_update(subscription: Book, data: TradingPairBook):
    order_book.update(subscription["symbol"], data)

@bfx.wss.on("checksum")
async def on_checksum(subscription: Book, value: int):
    symbol = subscription["symbol"]

    if order_book.verify(symbol, value):
        order_book.cooldown[symbol] = False
    elif not order_book.cooldown[symbol]:
        print("Mismatch between local and remote checksums: "
            f"restarting book for symbol <{symbol}>...")

        await bfx.wss.resubscribe(sub_id=subscription["subId"])

        order_book.cooldown[symbol] = True

bfx.wss.run()
