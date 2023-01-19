from typing import TypedDict, Optional

__all__ = [
    "Ticker",
    "Trades",
    "Book",
    "Candles",
    "Status"
]

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
    subId: int
    pair: str

class Candles(TypedDict):
    chanId: int
    key: str

class Status(TypedDict):
    chanId: int
    key: str