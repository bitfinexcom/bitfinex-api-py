from typing import TypedDict, Union, Optional

__all__ = [
    "Subscription",

    "Ticker",
    "Trades",
    "Book",
    "Candles",
    "Status"
]

_Header = TypedDict("_Header", { "event": str, "channel": str, "subId": str })

Subscription = Union["Ticker", "Trades", "Book", "Candles", "Status"]

class Ticker(TypedDict):
    chanId: int; symbol: str
    pair: Optional[str]
    currency: Optional[str]

class Trades(TypedDict):
    chanId: int; symbol: str
    pair: Optional[str]
    currency: Optional[str]

class Book(TypedDict):
    chanId: int
    symbol: str
    prec: str
    freq: str
    len: str
    pair: str

class Candles(TypedDict):
    chanId: int
    key: str

class Status(TypedDict):
    chanId: int
    key: str