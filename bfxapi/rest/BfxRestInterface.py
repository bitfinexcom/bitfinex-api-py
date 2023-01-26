import time, hmac, hashlib, json, requests

from decimal import Decimal
from datetime import datetime
from http import HTTPStatus

from typing import List, Union, Literal, Optional, Any, cast

from . import serializers

from .types import *
from .enums import Config, Sort, OrderType, FundingOfferType, Error
from .exceptions import ResourceNotFound, RequestParametersError, InvalidAuthenticationCredentials, UnknownGenericError

from .. utils.encoder import JSONEncoder

class BfxRestInterface(object):
    def __init__(self, host, API_KEY = None, API_SECRET = None):
        self.public = _RestPublicEndpoints(host=host)

        self.auth = _RestAuthenticatedEndpoints(host=host, API_KEY=API_KEY, API_SECRET=API_SECRET)

class _Requests(object):
    def __init__(self, host, API_KEY = None, API_SECRET = None):
        self.host, self.API_KEY, self.API_SECRET = host, API_KEY, API_SECRET

    def __build_authentication_headers(self, endpoint, data):
        nonce = str(int(time.time()) * 1000)

        path = f"/api/v2/{endpoint}{nonce}"

        if data != None: path += data

        signature = hmac.new(
            self.API_SECRET.encode("utf8"),
            path.encode("utf8"),
            hashlib.sha384 
        ).hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-signature": signature,
            "bfx-apikey": self.API_KEY
        }

    def _GET(self, endpoint, params = None):
        response = requests.get(f"{self.host}/{endpoint}", params=params)
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

            if data[1] == None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError(f"The server replied to the request with a generic error with message: <{data[2]}>.")

        return data

    def _POST(self, endpoint, params = None, data = None):
        headers = { "Content-Type": "application/json" }

        if isinstance(data, dict):
            data = json.dumps({ key: value for key, value in data.items() if value != None}, cls=JSONEncoder)

        if self.API_KEY and self.API_SECRET:
            headers = { **headers, **self.__build_authentication_headers(endpoint, data) }

        response = requests.post(f"{self.host}/{endpoint}", params=params, data=data, headers=headers)
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

            if data[1] == Error.ERR_AUTH_FAIL:
                raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")

            if data[1] == None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError(f"The server replied to the request with a generic error with message: <{data[2]}>.")

        return data

class _RestPublicEndpoints(_Requests):
    def get_platform_status(self) -> PlatformStatus:
        return serializers.PlatformStatus.parse(*self._GET("platform/status"))

    def get_tickers(self, symbols: List[str]) -> List[Union[TradingPairTicker, FundingCurrencyTicker]]:
        data = self._GET("tickers", params={ "symbols": ",".join(symbols) })
        
        parsers = { "t": serializers.TradingPairTicker.parse, "f": serializers.FundingCurrencyTicker.parse }
        
        return [ cast(Union[TradingPairTicker, FundingCurrencyTicker], parsers[sub_data[0][0]](*sub_data)) for sub_data in data ]

    def get_t_tickers(self, pairs: Union[List[str], Literal["ALL"]]) -> List[TradingPairTicker]:
        if isinstance(pairs, str) and pairs == "ALL":
            return [ cast(TradingPairTicker, sub_data) for sub_data in self.get_tickers([ "ALL" ]) if cast(str, sub_data.SYMBOL).startswith("t") ]

        data = self.get_tickers([ "t" + pair for pair in pairs ])

        return cast(List[TradingPairTicker], data)

    def get_f_tickers(self, currencies: Union[List[str], Literal["ALL"]]) -> List[FundingCurrencyTicker]:
        if isinstance(currencies, str) and currencies == "ALL":
            return [ cast(FundingCurrencyTicker, sub_data) for sub_data in self.get_tickers([ "ALL" ]) if cast(str, sub_data.SYMBOL).startswith("f") ]

        data = self.get_tickers([ "f" + currency for currency in currencies ])

        return cast(List[FundingCurrencyTicker], data)

    def get_t_ticker(self, pair: str) -> TradingPairTicker:
        return serializers.TradingPairTicker.parse(*self._GET(f"ticker/t{pair}"), skip=["SYMBOL"])

    def get_f_ticker(self, currency: str) -> FundingCurrencyTicker:
        return serializers.FundingCurrencyTicker.parse(*self._GET(f"ticker/f{currency}"), skip=["SYMBOL"])

    def get_tickers_history(self, symbols: List[str], start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[TickersHistory]:
        params = {
            "symbols": ",".join(symbols),
            "start": start, "end": end,
            "limit": limit
        }

        data = self._GET("tickers/hist", params=params)
        
        return [ serializers.TickersHistory.parse(*sub_data) for sub_data in data ]

    def get_t_trades(self, pair: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[Sort] = None) -> List[TradingPairTrade]:
        params = { "limit": limit, "start": start, "end": end, "sort": sort }
        data = self._GET(f"trades/{'t' + pair}/hist", params=params)
        return [ serializers.TradingPairTrade.parse(*sub_data) for sub_data in data ]

    def get_f_trades(self, currency: str, limit: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, sort: Optional[Sort] = None) -> List[FundingCurrencyTrade]:
        params = { "limit": limit, "start": start, "end": end, "sort": sort }
        data = self._GET(f"trades/{'f' + currency}/hist", params=params)
        return [ serializers.FundingCurrencyTrade.parse(*sub_data) for sub_data in data ]

    def get_t_book(self, pair: str, precision: Literal["P0", "P1", "P2", "P3", "P4"], len: Optional[Literal[1, 25, 100]] = None) -> List[TradingPairBook]:
        return [ serializers.TradingPairBook.parse(*sub_data) for sub_data in self._GET(f"book/{'t' + pair}/{precision}", params={ "len": len }) ]

    def get_f_book(self, currency: str, precision: Literal["P0", "P1", "P2", "P3", "P4"], len: Optional[Literal[1, 25, 100]] = None) -> List[FundingCurrencyBook]:
        return [ serializers.FundingCurrencyBook.parse(*sub_data) for sub_data in self._GET(f"book/{'f' + currency}/{precision}", params={ "len": len }) ]

    def get_t_raw_book(self, pair: str, len: Optional[Literal[1, 25, 100]] = None) -> List[TradingPairRawBook]:
        return [ serializers.TradingPairRawBook.parse(*sub_data) for sub_data in self._GET(f"book/{'t' + pair}/R0", params={ "len": len }) ]

    def get_f_raw_book(self, currency: str, len: Optional[Literal[1, 25, 100]] = None) -> List[FundingCurrencyRawBook]:
        return [ serializers.FundingCurrencyRawBook.parse(*sub_data) for sub_data in self._GET(f"book/{'f' + currency}/R0", params={ "len": len }) ]

    def get_stats_hist(
        self, 
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Statistic]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"stats1/{resource}/hist", params=params)
        return [ serializers.Statistic.parse(*sub_data) for sub_data in data ]

    def get_stats_last(
        self, 
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Statistic:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"stats1/{resource}/last", params=params)
        return serializers.Statistic.parse(*data)

    def get_candles_hist(
        self,
        symbol: str, tf: str = "1m",
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Candle]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"candles/trade:{tf}:{symbol}/hist", params=params)
        return [ serializers.Candle.parse(*sub_data) for sub_data in data ]

    def get_candles_last(
        self,
        symbol: str, tf: str = "1m",
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Candle:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"candles/trade:{tf}:{symbol}/last", params=params)
        return serializers.Candle.parse(*data)

    def get_derivatives_status(self, keys: Union[List[str], Literal["ALL"]]) -> List[DerivativesStatus]:
        if keys == "ALL":
            params = { "keys": "ALL" }
        else:  params = { "keys": ",".join(keys) }

        data = self._GET(f"status/deriv", params=params)

        return [ serializers.DerivativesStatus.parse(*sub_data) for sub_data in data ]

    def get_derivatives_status_history(
        self, 
        type: str, symbol: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> List[DerivativesStatus]: 
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self._GET(f"status/{type}/{symbol}/hist", params=params)

        return [ serializers.DerivativesStatus.parse(*sub_data, skip=[ "KEY" ]) for sub_data in data ]

    def get_liquidations(self, sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Liquidation]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }

        data = self._GET("liquidations/hist", params=params)

        return [ serializers.Liquidation.parse(*sub_data[0]) for sub_data in data ]

    def get_seed_candles(self, symbol: str, tf: str = '1m', sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Candle]:

        params = {"sort": sort, "start": start, "end": end, "limit": limit}

        data = self._GET(f"candles/trade:{tf}:{symbol}/hist?limit={limit}&start={start}&end={end}&sort={sort}", params=params)

        return [ serializers.Candle.parse(*sub_data) for sub_data in data ]

    def get_leaderboards_hist(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Leaderboard]:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"rankings/{resource}/hist", params=params)
        return [ serializers.Leaderboard.parse(*sub_data) for sub_data in data ]

    def get_leaderboards_last(
        self,
        resource: str,
        sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None
    ) -> Leaderboard:
        params = { "sort": sort, "start": start, "end": end, "limit": limit }
        data = self._GET(f"rankings/{resource}/last", params=params)
        return serializers.Leaderboard.parse(*data)

    def get_funding_stats(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingStatistic]:
        params = { "start": start, "end": end, "limit": limit }

        data = self._GET(f"funding/stats/{symbol}/hist", params=params)

        return [ serializers.FundingStatistic.parse(*sub_data) for sub_data in data ]

    def conf(self, config: Config) -> Any:
        return self._GET(f"conf/{config}")[0]

    def get_pulse_profile(self, nickname: str) -> PulseProfile:
        return serializers.PulseProfile.parse(*self._GET(f"pulse/profile/{nickname}"))

    def get_pulse_history(self, end: Optional[str] = None, limit: Optional[int] = None) -> List[PulseMessage]:
        messages = list()

        for subdata in self._GET("pulse/hist", params={ "end": end, "limit": limit }):
            subdata[18] = subdata[18][0]
            message = serializers.PulseMessage.parse(*subdata)
            messages.append(message)

        return messages

    def get_trading_market_average_price(self, symbol: str, amount: Union[Decimal, float, str], price_limit: Optional[Union[Decimal, float, str]] = None) -> TradingMarketAveragePrice:
        data = {
            "symbol": symbol, "amount": amount, "price_limit": price_limit
        }

        return serializers.TradingMarketAveragePrice.parse(*self._POST("calc/trade/avg", data=data))

    def get_funding_market_average_price(self, symbol: str, amount: Union[Decimal, float, str], period: int, rate_limit: Optional[Union[Decimal, float, str]] = None) -> FundingMarketAveragePrice:
        data = {
            "symbol": symbol, "amount": amount, "period": period,
            "rate_limit": rate_limit
        }

        return serializers.FundingMarketAveragePrice.parse(*self._POST("calc/trade/avg", data=data))

    def get_fx_rate(self, ccy1: str, ccy2: str) -> FxRate:
        return serializers.FxRate.parse(*self._POST("calc/fx", data={ "ccy1": ccy1, "ccy2": ccy2 }))

class _RestAuthenticatedEndpoints(_Requests):
    def get_wallets(self) -> List[Wallet]:
        return [ serializers.Wallet.parse(*sub_data) for sub_data in self._POST("auth/r/wallets") ]

    def get_orders(self, symbol: Optional[str] = None, ids: Optional[List[str]] = None) -> List[Order]:
        endpoint = "auth/r/orders"

        if symbol != None:
            endpoint += f"/{symbol}"

        return [ serializers.Order.parse(*sub_data) for sub_data in self._POST(endpoint, data={ "id": ids }) ]

    def get_positions(self) -> List[Position]:
        return [ serializers.Position.parse(*sub_data) for sub_data in self._POST("auth/r/positions") ]

    def submit_order(self, type: OrderType, symbol: str, amount: Union[Decimal, float, str], 
                     price: Optional[Union[Decimal, float, str]] = None, lev: Optional[int] = None, 
                     price_trailing: Optional[Union[Decimal, float, str]] = None, price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_oco_stop: Optional[Union[Decimal, float, str]] = None,
                     gid: Optional[int] = None, cid: Optional[int] = None,
                     flags: Optional[int] = 0, tif: Optional[Union[datetime, str]] = None, meta: Optional[JSON] = None) -> Notification[Order]:
        data = {
            "type": type, "symbol": symbol, "amount": amount,
            "price": price, "lev": lev,
            "price_trailing": price_trailing, "price_aux_limit": price_aux_limit, "price_oco_stop": price_oco_stop,
            "gid": gid, "cid": cid,
            "flags": flags, "tif": tif, "meta": meta
        }
        
        return serializers._Notification[Order](serializer=serializers.Order).parse(*self._POST("auth/w/order/submit", data=data))

    def update_order(self, id: int, amount: Optional[Union[Decimal, float, str]] = None, price: Optional[Union[Decimal, float, str]] = None,
                     cid: Optional[int] = None, cid_date: Optional[str] = None, gid: Optional[int] = None,
                     flags: Optional[int] = 0, lev: Optional[int] = None, delta: Optional[Union[Decimal, float, str]] = None,
                     price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_trailing: Optional[Union[Decimal, float, str]] = None, tif: Optional[Union[datetime, str]] = None) -> Notification[Order]:
        data = {
            "id": id, "amount": amount, "price": price,
            "cid": cid, "cid_date": cid_date, "gid": gid,
            "flags": flags, "lev": lev, "delta": delta,
            "price_aux_limit": price_aux_limit, "price_trailing": price_trailing, "tif": tif
        }
        
        return serializers._Notification[Order](serializer=serializers.Order).parse(*self._POST("auth/w/order/update", data=data))

    def cancel_order(self, id: Optional[int] = None, cid: Optional[int] = None, cid_date: Optional[str] = None) -> Notification[Order]:
        data = { 
            "id": id, 
            "cid": cid, 
            "cid_date": cid_date 
        }

        return serializers._Notification[Order](serializer=serializers.Order).parse(*self._POST("auth/w/order/cancel", data=data))

    def cancel_order_multi(self, ids: Optional[List[int]] = None, cids: Optional[List[Tuple[int, str]]] = None, gids: Optional[List[int]] = None, all: bool = False) -> Notification[List[Order]]:
        data = {
            "ids": ids,
            "cids": cids,
            "gids": gids,

            "all": int(all)
        }

        return serializers._Notification[List[Order]](serializer=serializers.Order, iterate=True).parse(*self._POST("auth/w/order/cancel/multi", data=data))

    def get_orders_history(self, symbol: Optional[str] = None, ids: Optional[List[int]] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Order]:
        if symbol == None:
            endpoint = "auth/r/orders/hist"
        else: endpoint = f"auth/r/orders/{symbol}/hist"
        
        data = {
            "id": ids,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Order.parse(*sub_data) for sub_data in self._POST(endpoint, data=data) ]

    def get_trades_history(self, symbol: Optional[str] = None, sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Trade]:
        if symbol == None:
            endpoint = "auth/r/trades/hist"
        else: endpoint = f"auth/r/trades/{symbol}/hist"
        
        data = {
            "sort": sort,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Trade.parse(*sub_data) for sub_data in self._POST(endpoint, data=data) ]

    def get_order_trades(self, symbol: str, id: int) -> List[OrderTrade]:
        return [ serializers.OrderTrade.parse(*sub_data) for sub_data in self._POST(f"auth/r/order/{symbol}:{id}/trades") ]

    def get_ledgers(self, currency: str, category: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Ledger]:
        data = {
            "category": category,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Ledger.parse(*sub_data) for sub_data in self._POST(f"auth/r/ledgers/{currency}/hist", data=data) ]

    def get_funding_offers(self, symbol: Optional[str] = None) -> List[FundingOffer]:
        endpoint = "auth/r/funding/offers"

        if symbol != None:
            endpoint += f"/{symbol}"

        return [ serializers.FundingOffer.parse(*sub_data) for sub_data in self._POST(endpoint) ]

    def submit_funding_offer(self, type: FundingOfferType, symbol: str, amount: Union[Decimal, float, str],
                             rate: Union[Decimal, float, str], period: int,
                             flags: Optional[int] = 0) -> Notification[FundingOffer]:
        data = {
            "type": type, "symbol": symbol, "amount": amount,
            "rate": rate, "period": period, 
            "flags": flags
        }

        return serializers._Notification[FundingOffer](serializer=serializers.FundingOffer).parse(*self._POST("auth/w/funding/offer/submit", data=data))

    def cancel_funding_offer(self, id: int) -> Notification[FundingOffer]:
        return serializers._Notification[FundingOffer](serializer=serializers.FundingOffer).parse(*self._POST("auth/w/funding/offer/cancel", data={ "id": id }))

    def get_funding_offers_history(self, symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingOffer]:
        if symbol == None:
            endpoint = "auth/r/funding/offers/hist"
        else: endpoint = f"auth/r/funding/offers/{symbol}/hist"

        data = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingOffer.parse(*sub_data) for sub_data in self._POST(endpoint, data=data) ]

    def get_funding_credits(self, symbol: Optional[str] = None) -> List[FundingCredit]:
        if symbol == None:
            endpoint = "auth/r/funding/credits"
        else: endpoint = f"auth/r/funding/credits/{symbol}"

        return [ serializers.FundingCredit.parse(*sub_data) for sub_data in self._POST(endpoint) ]

    def get_funding_credits_history(self, symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingCredit]:
        if symbol == None:
            endpoint = "auth/r/funding/credits/hist"
        else: endpoint = f"auth/r/funding/credits/{symbol}/hist"
        
        data = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingCredit.parse(*sub_data) for sub_data in self._POST(endpoint, data=data) ]

    def submit_wallet_transfer(self, from_wallet: str, to_wallet: str, currency: str, currency_to: str, amount: Union[Decimal, float, str]) -> Notification[Transfer]:
        data = {
            "from": from_wallet, "to": to_wallet,
            "currency": currency, "currency_to": currency_to,
            "amount": amount
        }

        return serializers._Notification[Transfer](serializer=serializers.Transfer).parse(*self._POST("auth/w/transfer", data=data))

    def submit_wallet_withdraw(self, wallet: str, method: str, address: str, amount: Union[Decimal, float, str]) -> Notification[Withdrawal]:
        data = {
            "wallet": wallet, "method": method,
            "address": address, "amount": amount,
        }

        return serializers._Notification[Withdrawal](serializer=serializers.Withdrawal).parse(*self._POST("auth/w/withdraw", data=data))

    def get_deposit_address(self, wallet: str, method: str, renew: bool = False) -> Notification[DepositAddress]:
        data = {
            "wallet": wallet,
            "method": method,
            "renew": int(renew)
        }

        return serializers._Notification[DepositAddress](serializer=serializers.DepositAddress).parse(*self._POST("auth/w/deposit/address", data=data))

    def get_deposit_invoice(self, wallet: str, currency: str, amount: Union[Decimal, float, str]) -> Invoice:
        data = {
            "wallet": wallet, "currency": currency,
            "amount": amount
        }

        return serializers.Invoice.parse(*self._POST("auth/w/deposit/invoice", data=data))

    def get_movements(self, currency: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Movement]:
        if currency == None:
            endpoint = "auth/r/movements/hist"
        else: endpoint = f"auth/r/movements/{currency}/hist"
        
        data = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Movement.parse(*sub_data) for sub_data in self._POST(endpoint, data=data) ]

    def get_symbol_margin_info(self, symbol: str) -> SymbolMarginInfo:
        response = self._POST(f"auth/r/info/margin/{symbol}")

        return serializers.SymbolMarginInfo.parse(*([response[1]] + response[2]))
    
    def get_all_symbols_margin_info(self) -> List[SymbolMarginInfo]:
        return [ serializers.SymbolMarginInfo.parse(*([sub_data[1]] + sub_data[2])) for sub_data in self._POST(f"auth/r/info/margin/sym_all") ]

    def get_base_margin_info(self) -> BaseMarginInfo:
        return serializers.BaseMarginInfo.parse(*(self._POST(f"auth/r/info/margin/base")[1]))

    def claim_position(self, id: int, amount: Optional[Union[Decimal, float, str]] = None) -> Notification[Claim]:
        return serializers._Notification[Claim](serializer=serializers.Claim).parse(*self._POST("auth/w/position/claim", data={ "id": id, "amount": amount }))

    def get_increase_position_info(self, symbol: str, amount: Union[Decimal, float, str]) -> IncreaseInfo:
        response = self._POST(f"auth/r/position/increase/info", data={ "symbol": symbol, "amount": amount })

        return serializers.IncreaseInfo.parse(*(
            response[0] + [response[1][0]] + response[1][1] + [response[1][2]] + response[4] + response[5]
        ))

    def increase_position(self, symbol: str, amount: Union[Decimal, float, str]) -> Notification[Increase]:
        return serializers._Notification[Increase](serializer=serializers.Increase).parse(*self._POST("auth/w/position/increase", data={ "symbol": symbol, "amount": amount }))

    def get_positions_history(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionHistory]:
        return [ serializers.PositionHistory.parse(*sub_data) for sub_data in self._POST("auth/r/positions/hist", data={ "start": start, "end": end, "limit": limit }) ]
    
    def get_positions_snapshot(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionSnapshot]:
        return [ serializers.PositionSnapshot.parse(*sub_data) for sub_data in self._POST("auth/r/positions/snap", data={ "start": start, "end": end, "limit": limit }) ]

    def get_positions_audit(self, ids: Optional[List[int]] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionAudit]:
        return [ serializers.PositionAudit.parse(*sub_data) for sub_data in self._POST("auth/r/positions/audit", data={ "ids": ids, "start": start, "end": end, "limit": limit }) ]
