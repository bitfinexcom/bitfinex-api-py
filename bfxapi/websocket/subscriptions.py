from typing import Literal, TypedDict, Union

Subscription = Union["Ticker", "Trades", "Book", "Candles", "Status"]

Channel = Literal["ticker", "trades", "book", "candles", "status"]


class Ticker(TypedDict):
    channel: Literal["ticker"]
    sub_id: str
    symbol: str


class Trades(TypedDict):
    channel: Literal["trades"]
    sub_id: str
    symbol: str


class Book(TypedDict):
    channel: Literal["book"]
    sub_id: str
    symbol: str
    prec: Literal["R0", "P0", "P1", "P2", "P3", "P4"]
    freq: Literal["F0", "F1"]
    len: Literal["1", "25", "100", "250"]


class Candles(TypedDict):
    channel: Literal["candles"]
    sub_id: str
    key: str


class Status(TypedDict):
    channel: Literal["status"]
    sub_id: str
    key: str
