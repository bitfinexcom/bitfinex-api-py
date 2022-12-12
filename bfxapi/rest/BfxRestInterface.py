import requests

from http import HTTPStatus

from typing import List, Union, Literal, Optional

from . import serializers
from .typings import *
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
        
        return [
            {
                "t": serializers.TradingPairTicker.parse,
                "f": serializers.FundingCurrencyTicker.parse
            }[subdata[0][0]](*subdata)

            for subdata in data
        ]

    def ticker(self, symbol: str) -> Union[TradingPairTicker, FundingCurrencyTicker]:
        data = self.__GET(f"ticker/{symbol}")

        return {
            "t": serializers.TradingPairTicker.parse,
            "f": serializers.FundingCurrencyTicker.parse
        }[symbol[0]](*data, skip=["SYMBOL"])

    def tickers_history(self, symbols: List[str], start: Optional[int] = None, end: Optional[int] = None, limit: Optional[int] = None) -> TickerHistories:
        params = {
            "symbols": ",".join(symbols),
            "start": start, "end": end,
            "limit": limit
        }

        data = self.__GET("tickers/hist", params=params)
        
        return [ serializers.TickerHistory.parse(*subdata) for subdata in data ]

    def trades(self, symbol: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[int] = None) -> Union[TradingPairTrades, FundingCurrencyTrades]:
        params = { "symbol": symbol, "limit": limit, "start": start, "end": end, "sort": sort }
        
        data = self.__GET(f"trades/{symbol}/hist", params=params)

        return [
            {
                "t": serializers.TradingPairTrade.parse,
                "f": serializers.FundingCurrencyTrade.parse
            }[symbol[0]](*subdata)

            for subdata in data
        ]

    def book(self, symbol: str, precision: str, len: Optional[int] = None) -> Union[TradingPairBooks, FundingCurrencyBooks, TradingPairRawBooks, FundingCurrencyRawBooks]:
        data = self.__GET(f"book/{symbol}/{precision}", params={ "len": len })
        
        return [
            {
                "t": precision == "R0" and serializers.TradingPairRawBook.parse or serializers.TradingPairBook.parse,
                "f": precision == "R0" and serializers.FundingCurrencyRawBook.parse or serializers.FundingCurrencyBook.parse,
            }[symbol[0]](*subdata)

            for subdata in data
        ]

    def stats(
        self, 
        resource: str, section: Literal["hist", "last"],
        sort: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Union[Stat, Stats]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET(f"stats1/{resource}/{section}", params=params)

        if section == "last":
            return serializers.Stat.parse(*data)
        return [ serializers.Stat.parse(*subdata) for subdata in data ]

    def candles(
        self,
        resource: str, section: Literal["hist", "last"],
        sort: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Union[Candle, Candles]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET(f"candles/{resource}/{section}", params=params)

        if section == "last":
            return serializers.Candle.parse(*data)
        return [ serializers.Candle.parse(*subdata) for subdata in data ]

    def derivatives_status(self, type: str, keys: List[str] = None) -> DerivativeStatuses:
        params = { "keys": ",".join(keys) }

        data = self.__GET(f"status/{type}", params=params)

        return [ serializers.DerivativesStatus.parse(*subdata) for subdata in data ]

    def derivatives_status_history(
        self, 
        type: str, symbol: str,
        sort: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> DerivativeStatuses: 
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET(f"status/{type}/{symbol}/hist", params=params)

        return [ serializers.DerivativesStatus.parse(*subdata, skip=[ "KEY" ]) for subdata in data ]

    def liquidations(self, sort: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> Liquidations:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self.__GET("liquidations/hist", params=params)

        return [ serializers.Liquidation.parse(*subdata[0]) for subdata in data ]