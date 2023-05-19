from typing import TypedDict, \
    Union, Literal, Optional

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

Subscription = Union["_Ticker", "_Trades", "_Book", "_Candles", "_Status"]

_Channel = Literal["ticker", "trades", "book", "candles", "status"]

_Header = TypedDict("_Header", {
    "event": Literal["subscribed"],
    "channel": _Channel,
    "chanId": int
})

#pylint: disable-next=inherit-non-class
class _Ticker(Ticker, _Header):
    pass

#pylint: disable-next=inherit-non-class
class _Trades(Trades, _Header):
    pass

#pylint: disable-next=inherit-non-class
class _Book(Book, _Header):
    pass

#pylint: disable-next=inherit-non-class
class _Candles(Candles, _Header):
    pass

#pylint: disable-next=inherit-non-class
class _Status(Status, _Header):
    pass
