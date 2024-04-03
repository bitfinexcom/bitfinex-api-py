from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Union, cast

from bfxapi.rest._interface import Interface
from bfxapi.types import (
    Candle,
    DerivativesStatus,
    FundingCurrencyBook,
    FundingCurrencyRawBook,
    FundingCurrencyTicker,
    FundingCurrencyTrade,
    FundingMarketAveragePrice,
    FundingStatistic,
    FxRate,
    Leaderboard,
    Liquidation,
    PlatformStatus,
    PulseMessage,
    PulseProfile,
    Statistic,
    TickersHistory,
    TradingMarketAveragePrice,
    TradingPairBook,
    TradingPairRawBook,
    TradingPairTicker,
    TradingPairTrade,
    serializers,
)


class RestPublicEndpoints(Interface):
    def conf(self, config: str) -> Any:
        return self._m.get(f"conf/{config}")[0]

    def get_platform_status(self) -> PlatformStatus:
        return serializers.PlatformStatus.parse(*self._m.get("platform/status"))

    def get_tickers(
        self, symbols: List[str]
    ) -> Dict[str, Union[TradingPairTicker, FundingCurrencyTicker]]:
        data = self._m.get("tickers", params={"symbols": ",".join(symbols)})

        parsers = {
            "t": serializers.TradingPairTicker.parse,
            "f": serializers.FundingCurrencyTicker.parse,
        }

        return {
            symbol: cast(
                Union[TradingPairTicker, FundingCurrencyTicker],
                parsers[symbol[0]](*sub_data),
            )
            for sub_data in data
            if (symbol := sub_data.pop(0))
        }

    def get_t_tickers(
        self, symbols: Union[List[str], Literal["ALL"]]
    ) -> Dict[str, TradingPairTicker]:
        if isinstance(symbols, str) and symbols == "ALL":
            return {
                symbol: cast(TradingPairTicker, sub_data)
                for symbol, sub_data in self.get_tickers(["ALL"]).items()
                if symbol.startswith("t")
            }

        data = self.get_tickers(list(symbols))

        return cast(Dict[str, TradingPairTicker], data)

    def get_f_tickers(
        self, symbols: Union[List[str], Literal["ALL"]]
    ) -> Dict[str, FundingCurrencyTicker]:
        if isinstance(symbols, str) and symbols == "ALL":
            return {
                symbol: cast(FundingCurrencyTicker, sub_data)
                for symbol, sub_data in self.get_tickers(["ALL"]).items()
                if symbol.startswith("f")
            }

        data = self.get_tickers(list(symbols))

        return cast(Dict[str, FundingCurrencyTicker], data)

    def get_t_ticker(self, symbol: str) -> TradingPairTicker:
        return serializers.TradingPairTicker.parse(*self._m.get(f"ticker/{symbol}"))

    def get_f_ticker(self, symbol: str) -> FundingCurrencyTicker:
        return serializers.FundingCurrencyTicker.parse(*self._m.get(f"ticker/{symbol}"))

    def get_tickers_history(
        self,
        symbols: List[str],
        *,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[TickersHistory]:
        return [
            serializers.TickersHistory.parse(*sub_data)
            for sub_data in self._m.get(
                "tickers/hist",
                params={
                    "symbols": ",".join(symbols),
                    "start": start,
                    "end": end,
                    "limit": limit,
                },
            )
        ]

    def get_t_trades(
        self,
        pair: str,
        *,
        limit: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[int] = None,
    ) -> List[TradingPairTrade]:
        params = {"limit": limit, "start": start, "end": end, "sort": sort}
        data = self._m.get(f"trades/{pair}/hist", params=params)
        return [serializers.TradingPairTrade.parse(*sub_data) for sub_data in data]

    def get_f_trades(
        self,
        currency: str,
        *,
        limit: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[int] = None,
    ) -> List[FundingCurrencyTrade]:
        params = {"limit": limit, "start": start, "end": end, "sort": sort}
        data = self._m.get(f"trades/{currency}/hist", params=params)
        return [serializers.FundingCurrencyTrade.parse(*sub_data) for sub_data in data]

    def get_t_book(
        self,
        pair: str,
        precision: Literal["P0", "P1", "P2", "P3", "P4"],
        *,
        len: Optional[Literal[1, 25, 100]] = None,
    ) -> List[TradingPairBook]:
        return [
            serializers.TradingPairBook.parse(*sub_data)
            for sub_data in self._m.get(f"book/{pair}/{precision}", params={"len": len})
        ]

    def get_f_book(
        self,
        currency: str,
        precision: Literal["P0", "P1", "P2", "P3", "P4"],
        *,
        len: Optional[Literal[1, 25, 100]] = None,
    ) -> List[FundingCurrencyBook]:
        return [
            serializers.FundingCurrencyBook.parse(*sub_data)
            for sub_data in self._m.get(
                f"book/{currency}/{precision}", params={"len": len}
            )
        ]

    def get_t_raw_book(
        self, pair: str, *, len: Optional[Literal[1, 25, 100]] = None
    ) -> List[TradingPairRawBook]:
        return [
            serializers.TradingPairRawBook.parse(*sub_data)
            for sub_data in self._m.get(f"book/{pair}/R0", params={"len": len})
        ]

    def get_f_raw_book(
        self, currency: str, *, len: Optional[Literal[1, 25, 100]] = None
    ) -> List[FundingCurrencyRawBook]:
        return [
            serializers.FundingCurrencyRawBook.parse(*sub_data)
            for sub_data in self._m.get(f"book/{currency}/R0", params={"len": len})
        ]

    def get_stats_hist(
        self,
        resource: str,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Statistic]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"stats1/{resource}/hist", params=params)
        return [serializers.Statistic.parse(*sub_data) for sub_data in data]

    def get_stats_last(
        self,
        resource: str,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Statistic:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"stats1/{resource}/last", params=params)
        return serializers.Statistic.parse(*data)

    def get_candles_hist(
        self,
        symbol: str,
        tf: str = "1m",
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Candle]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"candles/trade:{tf}:{symbol}/hist", params=params)
        return [serializers.Candle.parse(*sub_data) for sub_data in data]

    def get_candles_last(
        self,
        symbol: str,
        tf: str = "1m",
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Candle:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"candles/trade:{tf}:{symbol}/last", params=params)
        return serializers.Candle.parse(*data)

    def get_derivatives_status(
        self, keys: Union[List[str], Literal["ALL"]]
    ) -> Dict[str, DerivativesStatus]:
        if keys == "ALL":
            params = {"keys": "ALL"}
        else:
            params = {"keys": ",".join(keys)}

        data = self._m.get("status/deriv", params=params)

        return {
            key: serializers.DerivativesStatus.parse(*sub_data)
            for sub_data in data
            if (key := sub_data.pop(0))
        }

    def get_derivatives_status_history(
        self,
        key: str,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[DerivativesStatus]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"status/deriv/{key}/hist", params=params)
        return [serializers.DerivativesStatus.parse(*sub_data) for sub_data in data]

    def get_liquidations(
        self,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Liquidation]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get("liquidations/hist", params=params)
        return [serializers.Liquidation.parse(*sub_data[0]) for sub_data in data]

    def get_seed_candles(
        self,
        symbol: str,
        tf: str = "1m",
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Candle]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"candles/trade:{tf}:{symbol}/hist", params=params)
        return [serializers.Candle.parse(*sub_data) for sub_data in data]

    def get_leaderboards_hist(
        self,
        resource: str,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Leaderboard]:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"rankings/{resource}/hist", params=params)
        return [serializers.Leaderboard.parse(*sub_data) for sub_data in data]

    def get_leaderboards_last(
        self,
        resource: str,
        *,
        sort: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Leaderboard:
        params = {"sort": sort, "start": start, "end": end, "limit": limit}
        data = self._m.get(f"rankings/{resource}/last", params=params)
        return serializers.Leaderboard.parse(*data)

    def get_funding_stats(
        self,
        symbol: str,
        *,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[FundingStatistic]:
        params = {"start": start, "end": end, "limit": limit}
        data = self._m.get(f"funding/stats/{symbol}/hist", params=params)
        return [serializers.FundingStatistic.parse(*sub_data) for sub_data in data]

    def get_pulse_profile_details(self, nickname: str) -> PulseProfile:
        return serializers.PulseProfile.parse(*self._m.get(f"pulse/profile/{nickname}"))

    def get_pulse_message_history(
        self, *, end: Optional[str] = None, limit: Optional[int] = None
    ) -> List[PulseMessage]:
        messages = []

        for sub_data in self._m.get("pulse/hist", params={"end": end, "limit": limit}):
            sub_data[18] = sub_data[18][0]
            message = serializers.PulseMessage.parse(*sub_data)
            messages.append(message)

        return messages

    def get_trading_market_average_price(
        self,
        symbol: str,
        amount: Union[str, float, Decimal],
        *,
        price_limit: Optional[Union[str, float, Decimal]] = None,
    ) -> TradingMarketAveragePrice:
        return serializers.TradingMarketAveragePrice.parse(
            *self._m.post(
                "calc/trade/avg",
                body={"symbol": symbol, "amount": amount, "price_limit": price_limit},
            )
        )

    def get_funding_market_average_price(
        self,
        symbol: str,
        amount: Union[str, float, Decimal],
        period: int,
        *,
        rate_limit: Optional[Union[str, float, Decimal]] = None,
    ) -> FundingMarketAveragePrice:
        return serializers.FundingMarketAveragePrice.parse(
            *self._m.post(
                "calc/trade/avg",
                body={
                    "symbol": symbol,
                    "amount": amount,
                    "period": period,
                    "rate_limit": rate_limit,
                },
            )
        )

    def get_fx_rate(self, ccy1: str, ccy2: str) -> FxRate:
        return serializers.FxRate.parse(
            *self._m.post("calc/fx", body={"ccy1": ccy1, "ccy2": ccy2})
        )
