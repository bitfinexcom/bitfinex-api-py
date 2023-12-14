# python -c "import examples.websocket.public.order_book"

import zlib
from collections import OrderedDict
from typing import Any, Dict, List, cast

from bfxapi import Client
from bfxapi.types import TradingPairBook
from bfxapi.websocket.subscriptions import Book


class OrderBook:
    def __init__(self, symbols: List[str]):
        self.__order_book = {
            symbol: {"bids": OrderedDict(), "asks": OrderedDict()} for symbol in symbols
        }

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

    def is_verifiable(self, symbol: str) -> bool:
        return (
            len(self.__order_book[symbol]["bids"]) >= 25
            and len(self.__order_book[symbol]["asks"]) >= 25
        )

    def clear(self, symbol: str) -> None:
        self.__order_book[symbol] = {"bids": OrderedDict(), "asks": OrderedDict()}


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

    if order_book.is_verifiable(symbol):
        if not order_book.verify(symbol, value):
            print(
                "Mismatch between local and remote checksums: "
                f"restarting book for symbol <{symbol}>..."
            )

            _subscription = cast(Dict[str, Any], subscription.copy())

            await bfx.wss.unsubscribe(sub_id=_subscription.pop("sub_id"))

            await bfx.wss.subscribe(**_subscription)

            order_book.clear(symbol)


bfx.wss.run()
