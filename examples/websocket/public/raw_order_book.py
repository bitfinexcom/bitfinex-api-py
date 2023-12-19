# python -c "import examples.websocket.public.raw_order_book"

import zlib
from collections import OrderedDict
from decimal import Decimal
from math import floor, log10
from typing import Any, Dict, List, cast

from bfxapi import Client
from bfxapi.types import TradingPairRawBook
from bfxapi.websocket.subscriptions import Book


def _format_float(value: float) -> str:
    """
    Format float numbers into a string compatible with the Bitfinex API.
    """

    def _find_exp(number: float) -> int:
        base10 = log10(abs(number))

        return floor(base10)

    if _find_exp(value) >= -6:
        return format(Decimal(repr(value)), "f")

    return str(value).replace("e-0", "e-")


class RawOrderBook:
    def __init__(self, symbols: List[str]):
        self.__raw_order_book = {
            symbol: {"bids": OrderedDict(), "asks": OrderedDict()} for symbol in symbols
        }

    def update(self, symbol: str, data: TradingPairRawBook) -> None:
        order_id, price, amount = data.order_id, data.price, data.amount

        kind = "bids" if amount > 0 else "asks"

        if price > 0:
            self.__raw_order_book[symbol][kind][order_id] = {
                "order_id": order_id,
                "price": price,
                "amount": amount,
            }

        if price == 0:
            if order_id in self.__raw_order_book[symbol][kind]:
                del self.__raw_order_book[symbol][kind][order_id]

    def verify(self, symbol: str, checksum: int) -> bool:
        values: List[int] = []

        bids = sorted(
            [
                (data["order_id"], data["price"], data["amount"])
                for _, data in self.__raw_order_book[symbol]["bids"].items()
            ],
            key=lambda data: (-data[1], data[0]),
        )

        asks = sorted(
            [
                (data["order_id"], data["price"], data["amount"])
                for _, data in self.__raw_order_book[symbol]["asks"].items()
            ],
            key=lambda data: (data[1], data[0]),
        )

        if len(bids) < 25 or len(asks) < 25:
            raise AssertionError("Not enough bids or asks (need at least 25).")

        for _i in range(25):
            bid, ask = bids[_i], asks[_i]
            values.extend([bid[0], bid[2]])
            values.extend([ask[0], ask[2]])

        local = ":".join(_format_float(value) for value in values)

        crc32 = zlib.crc32(local.encode("UTF-8"))

        return crc32 == checksum

    def is_verifiable(self, symbol: str) -> bool:
        return (
            len(self.__raw_order_book[symbol]["bids"]) >= 25
            and len(self.__raw_order_book[symbol]["asks"]) >= 25
        )

    def clear(self, symbol: str) -> None:
        self.__raw_order_book[symbol] = {"bids": OrderedDict(), "asks": OrderedDict()}


SYMBOLS = ["tLTCBTC", "tETHUSD", "tETHBTC"]

raw_order_book = RawOrderBook(symbols=SYMBOLS)

bfx = Client()


@bfx.wss.on("open")
async def on_open():
    for symbol in SYMBOLS:
        await bfx.wss.subscribe("book", symbol=symbol, prec="R0")


@bfx.wss.on("subscribed")
def on_subscribed(subscription):
    print(f"Subscription successful for symbol <{subscription['symbol']}>")


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

    if raw_order_book.is_verifiable(symbol):
        if not raw_order_book.verify(symbol, value):
            print(
                "Mismatch between local and remote checksums: "
                + f"restarting book for symbol <{symbol}>..."
            )

            _subscription = cast(Dict[str, Any], subscription.copy())

            await bfx.wss.unsubscribe(sub_id=_subscription.pop("sub_id"))

            await bfx.wss.subscribe(**_subscription)

            raw_order_book.clear(symbol)


bfx.wss.run()
