from typing import TypedDict, Union, Literal, Optional

_Channel = Literal[
    "ticker",
    "trades",
    "book",
    "candles",
    "status"
]

_Header = TypedDict("_Header", {
    "event": Literal["subscribed"],
    "channel": _Channel,
    "chanId": int
})

Subscription = Union[_Header, "Ticker", "Trades", "Book", "Candles", "Status"]

class Ticker(TypedDict):
    subId: str
    symbol: str
    pair: Optional[str]
    currency: Optional[str]

class Trades(TypedDict):
    subId: str
    symbol: str
    pair: Optional[str]
    currency: Optional[str]

class Book(TypedDict):
    subId: str
    symbol: str
    prec: str
    freq: str
    len: str
    pair: str

class Candles(TypedDict):
    subId: str
    key: str

class Status(TypedDict):
    subId: str
    key: str
