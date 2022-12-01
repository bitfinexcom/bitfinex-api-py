from typing import Generic, TypeVar, Iterable, Optional, List, Any

from . import typings

from .exceptions import BfxRestException

T = TypeVar("T")

class _Serializer(Generic[T]):
    def __init__(self, name: str, labels: List[str], IGNORE: List[str] = [ "_PLACEHOLDER" ]):
        self.name, self.__labels, self.__IGNORE = name, labels, IGNORE

    def __serialize(self, *args: Any, skip: Optional[List[str]]) -> Iterable[T]:
        labels = list(filter(lambda label: label not in (skip or list()), self.__labels))

        if len(labels) != len(args):
            raise BfxRestException("<labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(labels):
            if label not in self.__IGNORE:
                yield label, args[index]

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> T:
        return dict(self.__serialize(*values, skip=skip))

#region Serializers definition for Rest Public Endpoints

PlatformStatus = _Serializer[typings.PlatformStatus]("PlatformStatus", labels=[
    "OPERATIVE"
])

TradingPairTicker = _Serializer[typings.TradingPairTicker]("TradingPairTicker", labels=[
    "SYMBOL",
    "BID",
    "BID_SIZE",
    "ASK",
    "ASK_SIZE",
    "DAILY_CHANGE",
    "DAILY_CHANGE_RELATIVE",
    "LAST_PRICE",
    "VOLUME",
    "HIGH",
    "LOW"
])

FundingCurrencyTicker = _Serializer[typings.FundingCurrencyTicker]("FundingCurrencyTicker", labels=[
    "SYMBOL",
    "FRR",
    "BID",
    "BID_PERIOD",
    "BID_SIZE",
    "ASK",
    "ASK_PERIOD",
    "ASK_SIZE",
    "DAILY_CHANGE",
    "DAILY_CHANGE_RELATIVE",
    "LAST_PRICE",
    "VOLUME",
    "HIGH",
    "LOW",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FRR_AMOUNT_AVAILABLE"
])

TickerHistory = _Serializer[typings.TickerHistory]("TickerHistory", labels=[
    "SYMBOL",
    "BID",
    "_PLACEHOLDER",
    "ASK",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "MTS"
])

TradingPairTrade = _Serializer[typings.TradingPairTrade]("TradingPairTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "PRICE" 
])

FundingCurrencyTrade = _Serializer[typings.FundingCurrencyTrade]("FundingCurrencyTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "RATE", 
    "PERIOD" 
])

#endregion