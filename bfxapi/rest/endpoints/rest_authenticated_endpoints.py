from typing import List, Union, Literal, Optional

from ..types import *

from .. import serializers

from ..enums import Sort, OrderType, FundingOfferType
from decimal import Decimal
from datetime import datetime

from ..middleware import Middleware

class RestAuthenticatedEndpoints(Middleware):
    def get_user_info(self) -> UserInfo:
        return serializers.UserInfo.parse(*self._POST(f"auth/r/info/user"))

    def get_login_history(self) -> LoginHistory:
        return [ serializers.LoginHistory.parse(*sub_data) for sub_data in self._POST("auth/r/logins/hist") ]

    def get_balance_available_for_orders_or_offers(self, symbol: str, type: str, dir: Optional[int] = None, rate: Optional[str] = None, lev: Optional[str] = None) -> BalanceAvailable:
        return serializers.BalanceAvailable.parse(*self._POST("auth/calc/order/avail", body={
            "symbol": symbol, "type": type, "dir": dir,
            "rate": rate, "lev": lev
        }))

    def get_wallets(self) -> List[Wallet]:
        return [ serializers.Wallet.parse(*sub_data) for sub_data in self._POST("auth/r/wallets") ]

    def get_orders(self, symbol: Optional[str] = None, ids: Optional[List[str]] = None) -> List[Order]:
        endpoint = "auth/r/orders"

        if symbol != None:
            endpoint += f"/{symbol}"

        return [ serializers.Order.parse(*sub_data) for sub_data in self._POST(endpoint, body={ "id": ids }) ]

    def submit_order(self, type: OrderType, symbol: str, amount: Union[Decimal, float, str], 
                     price: Optional[Union[Decimal, float, str]] = None, lev: Optional[int] = None, 
                     price_trailing: Optional[Union[Decimal, float, str]] = None, price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_oco_stop: Optional[Union[Decimal, float, str]] = None,
                     gid: Optional[int] = None, cid: Optional[int] = None,
                     flags: Optional[int] = 0, tif: Optional[Union[datetime, str]] = None, meta: Optional[JSON] = None) -> Notification[Order]:
        body = {
            "type": type, "symbol": symbol, "amount": amount,
            "price": price, "lev": lev,
            "price_trailing": price_trailing, "price_aux_limit": price_aux_limit, "price_oco_stop": price_oco_stop,
            "gid": gid, "cid": cid,
            "flags": flags, "tif": tif, "meta": meta
        }
        
        return serializers._Notification[Order](serializers.Order).parse(*self._POST("auth/w/order/submit", body=body))

    def update_order(self, id: int, amount: Optional[Union[Decimal, float, str]] = None, price: Optional[Union[Decimal, float, str]] = None,
                     cid: Optional[int] = None, cid_date: Optional[str] = None, gid: Optional[int] = None,
                     flags: Optional[int] = 0, lev: Optional[int] = None, delta: Optional[Union[Decimal, float, str]] = None,
                     price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_trailing: Optional[Union[Decimal, float, str]] = None, tif: Optional[Union[datetime, str]] = None) -> Notification[Order]:
        body = {
            "id": id, "amount": amount, "price": price,
            "cid": cid, "cid_date": cid_date, "gid": gid,
            "flags": flags, "lev": lev, "delta": delta,
            "price_aux_limit": price_aux_limit, "price_trailing": price_trailing, "tif": tif
        }
        
        return serializers._Notification[Order](serializers.Order).parse(*self._POST("auth/w/order/update", body=body))

    def cancel_order(self, id: Optional[int] = None, cid: Optional[int] = None, cid_date: Optional[str] = None) -> Notification[Order]:
        body = { 
            "id": id, 
            "cid": cid, 
            "cid_date": cid_date 
        }

        return serializers._Notification[Order](serializers.Order).parse(*self._POST("auth/w/order/cancel", body=body))

    def cancel_order_multi(self, ids: Optional[List[int]] = None, cids: Optional[List[Tuple[int, str]]] = None, gids: Optional[List[int]] = None, all: bool = False) -> Notification[List[Order]]:
        body = {
            "ids": ids,
            "cids": cids,
            "gids": gids,

            "all": int(all)
        }

        return serializers._Notification[List[Order]](serializers.Order, is_iterable=True).parse(*self._POST("auth/w/order/cancel/multi", body=body))

    def get_orders_history(self, symbol: Optional[str] = None, ids: Optional[List[int]] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Order]:
        if symbol == None:
            endpoint = "auth/r/orders/hist"
        else: endpoint = f"auth/r/orders/{symbol}/hist"
        
        body = {
            "id": ids,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Order.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_order_trades(self, symbol: str, id: int) -> List[OrderTrade]:
        return [ serializers.OrderTrade.parse(*sub_data) for sub_data in self._POST(f"auth/r/order/{symbol}:{id}/trades") ]

    def get_trades_history(self, symbol: Optional[str] = None, sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Trade]:
        if symbol == None:
            endpoint = "auth/r/trades/hist"
        else: endpoint = f"auth/r/trades/{symbol}/hist"
        
        body = {
            "sort": sort,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Trade.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_ledgers(self, currency: str, category: Optional[int] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Ledger]:
        body = {
            "category": category,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Ledger.parse(*sub_data) for sub_data in self._POST(f"auth/r/ledgers/{currency}/hist", body=body) ]

    def get_base_margin_info(self) -> BaseMarginInfo:
        return serializers.BaseMarginInfo.parse(*(self._POST(f"auth/r/info/margin/base")[1]))

    def get_symbol_margin_info(self, symbol: str) -> SymbolMarginInfo:
        response = self._POST(f"auth/r/info/margin/{symbol}")
        data = [response[1]] + response[2]
        return serializers.SymbolMarginInfo.parse(*data)

    def get_all_symbols_margin_info(self) -> List[SymbolMarginInfo]:
        return [ serializers.SymbolMarginInfo.parse(*([sub_data[1]] + sub_data[2])) for sub_data in self._POST(f"auth/r/info/margin/sym_all") ]

    def get_positions(self) -> List[Position]:
       return [ serializers.Position.parse(*sub_data) for sub_data in self._POST("auth/r/positions") ]

    def claim_position(self, id: int, amount: Optional[Union[Decimal, float, str]] = None) -> Notification[PositionClaim]:
        return serializers._Notification[PositionClaim](serializers.PositionClaim).parse(
            *self._POST("auth/w/position/claim", body={ "id": id, "amount": amount })
        )

    def increase_position(self, symbol: str, amount: Union[Decimal, float, str]) -> Notification[PositionIncrease]:
        return serializers._Notification[PositionIncrease](serializers.PositionIncrease).parse(
            *self._POST("auth/w/position/increase", body={ "symbol": symbol, "amount": amount })
        )

    def get_increase_position_info(self, symbol: str, amount: Union[Decimal, float, str]) -> PositionIncreaseInfo:
        response = self._POST(f"auth/r/position/increase/info", body={ "symbol": symbol, "amount": amount })
        data = response[0] + [response[1][0]] + response[1][1] + [response[1][2]] + response[4] + response[5]
        return serializers.PositionIncreaseInfo.parse(*data)

    def get_positions_history(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionHistory]:
        return [ serializers.PositionHistory.parse(*sub_data) for sub_data in self._POST("auth/r/positions/hist", body={ "start": start, "end": end, "limit": limit }) ]

    def get_positions_snapshot(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionSnapshot]:
        return [ serializers.PositionSnapshot.parse(*sub_data) for sub_data in self._POST("auth/r/positions/snap", body={ "start": start, "end": end, "limit": limit }) ]

    def get_positions_audit(self, ids: Optional[List[int]] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[PositionAudit]:
        return [ serializers.PositionAudit.parse(*sub_data) for sub_data in self._POST("auth/r/positions/audit", body={ "ids": ids, "start": start, "end": end, "limit": limit }) ]

    def set_derivative_position_collateral(self, symbol: str, collateral: Union[Decimal, float, str]) -> DerivativePositionCollateral:
        return serializers.DerivativePositionCollateral.parse(*(self._POST("auth/w/deriv/collateral/set", body={ "symbol": symbol, "collateral": collateral })[0]))

    def get_derivative_position_collateral_limits(self, symbol: str) -> DerivativePositionCollateralLimits:
        return serializers.DerivativePositionCollateralLimits.parse(*self._POST("auth/calc/deriv/collateral/limits", body={ "symbol": symbol }))

    def get_funding_offers(self, symbol: Optional[str] = None) -> List[FundingOffer]:
        endpoint = "auth/r/funding/offers"

        if symbol != None:
            endpoint += f"/{symbol}"

        return [ serializers.FundingOffer.parse(*sub_data) for sub_data in self._POST(endpoint) ]

    def submit_funding_offer(self, type: FundingOfferType, symbol: str, amount: Union[Decimal, float, str],
                             rate: Union[Decimal, float, str], period: int,
                             flags: Optional[int] = 0) -> Notification[FundingOffer]:
        body = {
            "type": type, "symbol": symbol, "amount": amount,
            "rate": rate, "period": period, 
            "flags": flags
        }

        return serializers._Notification[FundingOffer](serializers.FundingOffer).parse(*self._POST("auth/w/funding/offer/submit", body=body))

    def cancel_funding_offer(self, id: int) -> Notification[FundingOffer]:
        return serializers._Notification[FundingOffer](serializers.FundingOffer).parse(*self._POST("auth/w/funding/offer/cancel", body={ "id": id }))

    def cancel_all_funding_offers(self, currency: str) -> Notification[Literal[None]]:
        return serializers._Notification[Literal[None]](None).parse(
            *self._POST("auth/w/funding/offer/cancel/all", body={ "currency": currency })
        )

    def submit_funding_close(self, id: int) -> Notification[Literal[None]]:
        return serializers._Notification[Literal[None]](None).parse(
            *self._POST("auth/w/funding/close", body={ "id": id })
        )

    def toggle_auto_renew(self, status: bool, currency: str, amount: Optional[str] = None, rate: Optional[int] = None, period: Optional[int] = None) -> Notification[FundingAutoRenew]:
        return serializers._Notification[FundingAutoRenew](serializers.FundingAutoRenew).parse(*self._POST("auth/w/funding/auto", body={
            "status": int(status),
            "currency": currency, "amount": amount,
            "rate": rate, "period": period
        }))

    def toggle_keep(self, type: Literal["credit", "loan"], ids: Optional[List[int]] = None, changes: Optional[Dict[int, bool]] = None) -> Notification[Literal[None]]:
        return serializers._Notification[Literal[None]](None).parse(*self._POST("auth/w/funding/keep", body={
            "type": type,
            "id": ids,
            "changes": changes
        }))

    def get_funding_offers_history(self, symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingOffer]:
        if symbol == None:
            endpoint = "auth/r/funding/offers/hist"
        else: endpoint = f"auth/r/funding/offers/{symbol}/hist"

        body = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingOffer.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_funding_loans(self, symbol: Optional[str] = None) -> List[FundingLoan]:
        if symbol == None:
            endpoint = "auth/r/funding/loans"
        else: endpoint = f"auth/r/funding/loans/{symbol}"

        return [ serializers.FundingLoan.parse(*sub_data) for sub_data in self._POST(endpoint) ]

    def get_funding_loans_history(self, symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingLoan]:
        if symbol == None:
            endpoint = "auth/r/funding/loans/hist"
        else: endpoint = f"auth/r/funding/loans/{symbol}/hist"
        
        body = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingLoan.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_funding_credits(self, symbol: Optional[str] = None) -> List[FundingCredit]:
        if symbol == None:
            endpoint = "auth/r/funding/credits"
        else: endpoint = f"auth/r/funding/credits/{symbol}"

        return [ serializers.FundingCredit.parse(*sub_data) for sub_data in self._POST(endpoint) ]

    def get_funding_credits_history(self, symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingCredit]:
        if symbol == None:
            endpoint = "auth/r/funding/credits/hist"
        else: endpoint = f"auth/r/funding/credits/{symbol}/hist"
        
        body = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingCredit.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_funding_trades_history(self, symbol: Optional[str] = None, sort: Optional[Sort] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[FundingTrade]:
        if symbol == None:
            endpoint = "auth/r/funding/trades/hist"
        else: endpoint = f"auth/r/funding/trades/{symbol}/hist"

        body = {
            "sort": sort,
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.FundingTrade.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]

    def get_funding_info(self, key: str) -> FundingInfo:
        response = self._POST(f"auth/r/info/funding/{key}")
        data = [response[1]] + response[2]
        return serializers.FundingInfo.parse(*data)

    def transfer_between_wallets(self, from_wallet: str, to_wallet: str, currency: str, currency_to: str, amount: Union[Decimal, float, str]) -> Notification[Transfer]:
        body = {
            "from": from_wallet, "to": to_wallet,
            "currency": currency, "currency_to": currency_to,
            "amount": amount
        }

        return serializers._Notification[Transfer](serializers.Transfer).parse(*self._POST("auth/w/transfer", body=body))

    def submit_wallet_withdrawal(self, wallet: str, method: str, address: str, amount: Union[Decimal, float, str]) -> Notification[Withdrawal]:
        return serializers._Notification[Withdrawal](serializers.Withdrawal).parse(*self._POST("auth/w/withdraw", body={
            "wallet": wallet, "method": method,
            "address": address, "amount": amount,
        }))

    def get_deposit_address(self, wallet: str, method: str, renew: bool = False) -> Notification[DepositAddress]:
        body = {
            "wallet": wallet,
            "method": method,
            "renew": int(renew)
        }

        return serializers._Notification[DepositAddress](serializers.DepositAddress).parse(*self._POST("auth/w/deposit/address", body=body))

    def generate_deposit_invoice(self, wallet: str, currency: str, amount: Union[Decimal, float, str]) -> Invoice:
        body = {
            "wallet": wallet, "currency": currency,
            "amount": amount
        }

        return serializers.Invoice.parse(*self._POST("auth/w/deposit/invoice", body=body))

    def get_movements(self, currency: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> List[Movement]:
        if currency == None:
            endpoint = "auth/r/movements/hist"
        else: endpoint = f"auth/r/movements/{currency}/hist"
        
        body = {
            "start": start, "end": end,
            "limit": limit
        }

        return [ serializers.Movement.parse(*sub_data) for sub_data in self._POST(endpoint, body=body) ]