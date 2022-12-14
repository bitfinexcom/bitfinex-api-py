import requests

from http import HTTPStatus

from typing import List, Union, Literal, Optional, Any, cast

from . import serializers

from .typings import *
from .enums import Config, Precision, Sort
from .exceptions import RequestParametersError, ResourceNotFound

class BfxRestInterface(object):
    def __init__(self, host):
        self.host = host

    def __GET(self, endpoint, params = None):
        response = requests.get(f"{self.host}/{endpoint}", params=params)
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == 10020:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

        return data

    def platform_status(self) -> PlatformStatus:
        return serializers.PlatformStatus.parse(*self.__GET("platform/status"))

    def tickers(self, symbols: List[str]) -> List[Union[TradingPairTicker, FundingCurrencyTicker]]:
        data = self.__GET("tickers", params={ "symbols": ",".join(symbols) })
        
        parsers = { "t": serializers.TradingPairTicker.parse, "f": serializers.FundingCurrencyTicker.parse }
        
        return [ parsers[subdata[0][0]](*subdata) for subdata in data ]

    def t_tickers(self, pairs: Union[List[str], Literal["ALL"]]) -> List[TradingPairTicker]:
        if isinstance(pairs, str) and pairs == "ALL":
            return [ subdata for subdata in self.tickers([ "ALL" ]) if subdata["SYMBOL"].startswith("t") ]

        data = self.tickers([ "t" + pair for pair in pairs ])

        return cast(List[TradingPairTicker], data)

    def f_tickers(self, currencies: Union[List[str], Literal["ALL"]]) -> List[FundingCurrencyTicker]:
        if isinstance(currencies, str) and currencies == "ALL":
            return [ subdata for subdata in self.tickers([ "ALL" ]) if subdata["SYMBOL"].startswith("f") ]

        data = self.tickers([ "f" + currency for currency in currencies ])

        return cast(List[FundingCurrencyTicker], data)

    def t_ticker(self, pair: str) -> TradingPairTicker:
        return serializers.TradingPairTicker.parse(*self.__GET(f"ticker/t{pair}"), skip=["SYMBOL"])

    def f_ticker(self, currency: str) -> FundingCurrencyTicker:
        return serializers.FundingCurrencyTicker.parse(*self.__GET(f"ticker/f{currency}"), skip=["SYMBOL"])

    def tickers_history(self, symbols: List[str], start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> TickersHistories:
        params = {
            "symbols": ",".join(symbols),
            "start": start, "end": end,
            "limit": limit
        }

        data = self.__GET("tickers/hist", params=params)
        
        return [ serializers.TickersHistory.parse(*subdata) for subdata in data ]

    def t_trades(self, pair: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[Sort] = None) -> TradingPairTrades:
        params = { "limit": limit, "start": start, "end": end, "sort": sort }
        data = self.__GET(f"trades/{'t' + pair}/hist", params=params)
        return [ serializers.TradingPairTrade.parse(*subdata) for subdata in data ]

    def f_trades(self, currency: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[Sort] = None) -> FundingCurrencyTrades:
        params = { "limit": limit, "start": start, "end": end, "sort": sort }
        data = self.__GET(f"trades/{'f' + currency}/hist", params=params)
        return [ serializers.FundingCurrencyTrade.parse(*subdata) for subdata in data ]

    def t_book(self, pair: str, precision: Literal["P0", "P1", "P2", "P3", "P4"], len: Optional[Literal[1, 25, 100]] = None) -> TradingPairBooks:
        return [ serializers.TradingPairBook.parse(*subdata) for subdata in self.__GET(f"book/{'t' + pair}/{precision}", params={ "len": len }) ]

    def f_book(self, currency: str, precision: Literal["P0", "P1", "P2", "P3", "P4"], len: Optional[Literal[1, 25, 100]] = None) -> FundingCurrencyBooks:
        return [ serializers.FundingCurrencyBook.parse(*subdata) for subdata in self.__GET(f"book/{'f' + currency}/{precision}", params={ "len": len }) ]

    def t_raw_book(self, pair: str, len: Optional[Literal[1, 25, 100]] = None) -> TradingPairRawBooks:
        return [ serializers.TradingPairRawBook.parse(*subdata) for subdata in self.__GET(f"book/{'t' + pair}/R0", params={ "len": len }) ]

    def f_raw_book(self, currency: str, len: Optional[Literal[1, 25, 100]] = None) -> FundingCurrencyRawBooks:
        return [ serializers.FundingCurrencyRawBook.parse(*subdata) for subdata in self.__GET(f"book/{'f' + currency}/R0", params={ "len": len }) ]

    def stats_hist(
        self, 
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Stats:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"stats1/{resource}/hist", params=params)
        return [ serializers.Stat.parse(*subdata) for subdata in data ]

    def stats_last(
        self, 
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Stat:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"stats1/{resource}/last", params=params)
        return serializers.Stat.parse(*data)

    def candles_hist(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Candles:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"candles/{resource}/hist", params=params)
        return [ serializers.Candle.parse(*subdata) for subdata in data ]

    def candles_last(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Candle:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"candles/{resource}/last", params=params)
        return serializers.Candle.parse(*data)

    def derivatives_status(self, type: str, keys: List[str]) -> DerivativeStatuses:
        params = { "keys": ",".join(keys) }

        data = self.__GET(f"status/{type}", params=params)

        return [ serializers.DerivativesStatus.parse(*subdata) for subdata in data ]

    def derivatives_status_history(
        self, 
        type: str, symbol: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> DerivativeStatuses: 
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET(f"status/{type}/{symbol}/hist", params=params)

        return [ serializers.DerivativesStatus.parse(*subdata, skip=[ "KEY" ]) for subdata in data ]

    def liquidations(self, sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> Liquidations:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET("liquidations/hist", params=params)

        return [ serializers.Liquidation.parse(*subdata[0]) for subdata in data ]

    def leaderboards_hist(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Leaderboards:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"rankings/{resource}/hist", params=params)
        return [ serializers.Leaderboard.parse(*subdata) for subdata in data ]

    def leaderboards_last(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Leaderboard:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self.__GET(f"rankings/{resource}/last", params=params)
        return serializers.Leaderboard.parse(*data)

    def funding_stats(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> FundingStats:
        params = { "start": start, "end": end, "limit": limit }

        data = self.__GET(f"funding/stats/{symbol}/hist", params=params)

        return [ serializers.FundingStat.parse(*subdata) for subdata in data ]

    def conf(self, config: Config) -> Any:
        return self.__GET(f"conf/{config}")[0]