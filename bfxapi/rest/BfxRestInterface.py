import requests

from http import HTTPStatus

from typing import List, Union, Optional

from . import serializers
from .typings import *
from .exceptions import RequestParametersError

class BfxRestInterface(object):
    def __init__(self, host):
        self.host = host

    def __GET(self, endpoint, params = None):
        data = requests.get(f"{self.host}/{endpoint}", params=params).json()
        
        if data[0] == "error":
            if data[1] == 10020:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

        return data

    def platform_status(self) -> PlatformStatus:
        return serializers.PlatformStatus.parse(*self.__GET("platform/status"))

    def tickers(self, symbols: List[str]) -> List[Union[TradingPairTicker, FundingCurrencyTicker]]:
        return [
            {
                "t": serializers.TradingPairTicker.parse,
                "f": serializers.FundingCurrencyTicker.parse
            }[subdata[0][0]](*subdata)

            for subdata in self.__GET("tickers", params={ "symbols": ",".join(symbols) })
        ]

    def ticker(self, symbol: str) -> Union[TradingPairTicker, FundingCurrencyTicker]:
        return {
            "t": serializers.TradingPairTicker.parse,
            "f": serializers.FundingCurrencyTicker.parse
        }[symbol[0]](*self.__GET(f"ticker/{symbol}"), skip=["SYMBOL"])

    def tickers_hist(self, symbols: List[str], start: Optional[int] = None, end: Optional[int] = None, limit: Optional[int] = None) -> TickerHistories:
        params = {
            "symbols": ",".join(symbols),
            "start": start, "end": end,
            "limit": limit
        }
        
        return [ serializers.TickerHistory.parse(*subdata) for subdata in self.__GET("tickers/hist", params=params) ]

    def trades(self, symbol: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[int] = None) -> Union[TradingPairTrades, FundingCurrencyTrades]:
        params = { "symbol": symbol, "limit": limit, "start": start, "end": end, "sort": sort }
        
        return [
            {
                "t": serializers.TradingPairTrade.parse,
                "f": serializers.FundingCurrencyTrade.parse
            }[symbol[0]](*subdata)

            for subdata in self.__GET(f"trades/{symbol}/hist", params=params)
        ]

    def book(self, symbol: str, precision: str, len: Optional[int]) -> Union[TradingPairBooks, FundingCurrencyBooks, TradingPairRawBooks, FundingCurrencyRawBooks]:
        return [
            {
                "t": precision == "R0" and serializers.TradingPairRawBook.parse or serializers.TradingPairBook.parse,
                "f": precision == "R0" and serializers.FundingCurrencyRawBook.parse or serializers.FundingCurrencyBook.parse,
            }[symbol[0]](*subdata)

            for subdata in self.__GET(f"book/{symbol}/{precision}", params={ "len": len })
        ]