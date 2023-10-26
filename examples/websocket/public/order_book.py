# python -c "import examples.websocket.public.order_book"

import zlib
from collections import OrderedDict
from typing import Dict, List

from bfxapi import Client
from bfxapi.types import TradingPairBook
from bfxapi.websocket.subscriptions import Book


class OrderBook:
    def __init__(self, symbols: List[str]):
        self.__order_book = {
            symbol: {"bids": OrderedDict(), "asks": OrderedDict()} for symbol in symbols
        }

        self.cooldown: Dict[str, bool] = {symbol: False for symbol in symbols}

    def update(self, symbol: str, data: TradingPairBook) -> None:
        price, count, amount = data.price, data.count, data.amount

        kind = "bids" if amount > 0 else "asks"

        if count > 0:
            self.__order_book[symbol][kind][price] = {
                "price": price,
                "count": count,
                "amount": amount,
            }

        if count == 0:
            if price in self.__order_book[symbol][kind]:
                del self.__order_book[symbol][kind][price]

    def verify(self, symbol: str, checksum: int) -> bool:
        values: List[int] = []

        bids = sorted(
            [
                (data["price"], data["count"], data["amount"])
                for _, data in self.__order_book[symbol]["bids"].items()
            ],
            key=lambda data: -data[0],
        )

        asks = sorted(
            [
                (data["price"], data["count"], data["amount"])
                for _, data in self.__order_book[symbol]["asks"].items()
            ],
            key=lambda data: data[0],
        )

        if len(bids) < 25 or len(asks) < 25:
            raise AssertionError("Not enough bids or asks (need at least 25).")

        for _i in range(25):
            bid, ask = bids[_i], asks[_i]
            values.extend([bid[0], bid[2]])
            values.extend([ask[0], ask[2]])

        local = ":".join(str(value) for value in values)

        crc32 = zlib.crc32(local.encode("UTF-8"))

        return crc32 == checksum


SYMBOLS = ["tLTCBTC", "tETHUSD", "tETHBTC"]

order_book = OrderBook(symbols=SYMBOLS)

bfx = Client()


@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe("book", symbol=symbol)


@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for symbol <{subscription['symbol']}>")


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
        print(
            "Mismatch between local and remote checksums: "
            f"restarting book for symbol <{symbol}>..."
        )

        await bfx.wss.resubscribe(sub_id=subscription["sub_id"])

        order_book.cooldown[symbol] = True


bfx.wss.run()
