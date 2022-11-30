from decimal import Decimal

from datetime import datetime

from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

int16 = int32 = int45 = int64 = int

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for subscription objects

class Subscriptions:
    TradingPairsTicker = TypedDict("Subscriptions.TradingPairsTicker", {
        "chanId": int,
        "symbol": str,
        "pair": str
    })

    FundingCurrenciesTicker = TypedDict("Subscriptions.FundingCurrenciesTicker", {
        "chanId": int,
        "symbol": str,
        "currency": str
    })

    TradingPairsTrades = TypedDict("Subscriptions.TradingPairsTrades", {
        "chanId": int,
        "symbol": str,
        "pair": str
    })

    FundingCurrenciesTrades = TypedDict("Subscriptions.FundingCurrenciesTrades", {
        "chanId": int,
        "symbol": str,
        "currency": str
    })

    Book = TypedDict("Subscriptions.Book", {
        "chanId": int,
        "symbol": str,
        "prec": str,
        "freq": str,
        "len": str,
        "subId": int,
        "pair": str
    })

    Candles = TypedDict("Subscriptions.Candles", {
        "chanId": int,
        "key": str
    })

    DerivativesStatus = TypedDict("Subscriptions.DerivativesStatus", {
        "chanId": int,
        "key": str
    })

#endregion

#region Type hinting for Websocket Public Channels

TradingPairTicker = TypedDict("TradingPairTicker", {
    "BID": float,
    "BID_SIZE": float,
    "ASK": float,
    "ASK_SIZE": float,
    "DAILY_CHANGE": float,
    "DAILY_CHANGE_RELATIVE": float,
    "LAST_PRICE": float,
    "VOLUME": float,
    "HIGH": float,
    "LOW": float
})

FundingCurrencyTicker = TypedDict("FundingCurrencyTicker", {
    "FRR": float,
    "BID": float,
    "BID_PERIOD": int,
    "BID_SIZE": float,
    "ASK": float,
    "ASK_PERIOD": int,
    "ASK_SIZE": float,
    "DAILY_CHANGE": float,
    "DAILY_CHANGE_RELATIVE": float,
    "LAST_PRICE": float,
    "VOLUME": float,
    "HIGH": float,
    "LOW": float,
    "FRR_AMOUNT_AVAILABLE": float
})

(TradingPairTrade, FundingCurrencyTrade) = (
    TypedDict("TradingPairTrade", { "ID": int, "MTS": int, "AMOUNT": float, "PRICE": float }),
    TypedDict("FundingCurrencyTrade", { "ID": int, "MTS": int, "AMOUNT": float, "RATE": float, "PERIOD": int })
)

(TradingPairTrades, FundingCurrencyTrades) = (List[TradingPairTrade], List[FundingCurrencyTrade])

(TradingPairBook, FundingCurrencyBook) = (
    TypedDict("TradingPairBook", { "PRICE": float, "COUNT": int, "AMOUNT": float }),
    TypedDict("FundingCurrencyBook", { "RATE": float, "PERIOD": int, "COUNT": int, "AMOUNT": float })
)

(TradingPairBooks, FundingCurrencyBooks) = (List[TradingPairBook], List[FundingCurrencyBook])

(TradingPairRawBook, FundingCurrencyRawBook) = (
    TypedDict("TradingPairRawBook", { "ORDER_ID": int, "PRICE": float, "AMOUNT": float }),
    TypedDict("FundingCurrencyRawBook", { "OFFER_ID": int, "PERIOD": int, "RATE": float, "AMOUNT": float }),
)

(TradingPairRawBooks, FundingCurrencyRawBooks) = (List[TradingPairRawBook], List[FundingCurrencyRawBook])

Candle = TypedDict("Candle", {
    "MTS": int,
    "OPEN": float,
    "CLOSE": float,
    "HIGH": float,
    "LOW": float,
    "VOLUME": float
})

Candles = List[Candle]

DerivativesStatus = TypedDict("DerivativesStatus", {
    "TIME_MS": int,
    "DERIV_PRICE": float,
    "SPOT_PRICE": float,
    "INSURANCE_FUND_BALANCE": float,
    "NEXT_FUNDING_EVT_TIMESTAMP_MS": int,
    "NEXT_FUNDING_ACCRUED": float,
    "NEXT_FUNDING_STEP": int,
    "CURRENT_FUNDING": float,
    "MARK_PRICE": float,
    "OPEN_INTEREST": float,
    "CLAMP_MIN": float,
    "CLAMP_MAX": float
})

#endregion

#region Type hinting for Websocket Authenticated Channels

Order = TypedDict("Order", {
    "ID": int,
    "GID": int,
    "CID": int,
    "SYMBOL": str,
    "MTS_CREATE": int,
    "MTS_UPDATE": int,
    "AMOUNT": float,
    "AMOUNT_ORIG": float,
    "ORDER_TYPE": str,
    "TYPE_PREV": str,
    "MTS_TIF": int,
    "FLAGS": int,
    "ORDER_STATUS": str,
    "PRICE": float,
    "PRICE_AVG": float,
    "PRICE_TRAILING": float,
    "PRICE_AUX_LIMIT": float,
    "NOTIFY": int,
    "HIDDEN": int,
    "PLACED_ID": int,
    "ROUTING": str,
    "META": JSON
})

Orders = List[Order]

Position = TypedDict("Position", {
    "SYMBOL": str,
    "STATUS": str,
    "AMOUNT": float,
    "BASE_PRICE": float,
    "MARGIN_FUNDING": float,
    "MARGIN_FUNDING_TYPE": int,
    "PL": float,
    "PL_PERC": float,
    "PRICE_LIQ": float,
    "LEVERAGE": float,
    "POSITION_ID": int,
    "MTS_CREATE": int,
    "MTS_UPDATE": int,
    "TYPE": int,
    "COLLATERAL": float,
    "COLLATERAL_MIN": float,
    "META": JSON,
})

Positions = List[Position]

TradeExecuted = TypedDict("TradeExecuted", {
    "ID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int,
    "ORDER_ID": int, 
    "EXEC_AMOUNT": float, 
    "EXEC_PRICE": float, 
    "ORDER_TYPE": str, 
    "ORDER_PRICE": float, 
    "MAKER":int,
    "CID": int
})

TradeExecutionUpdate = TypedDict("TradeExecutionUpdate", {
    "ID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int,
    "ORDER_ID": int, 
    "EXEC_AMOUNT": float, 
    "EXEC_PRICE": float, 
    "ORDER_TYPE": str, 
    "ORDER_PRICE": float, 
    "MAKER":int,
    "FEE": float,
    "FEE_CURRENCY": str,
    "CID": int
})

FundingOffer = TypedDict("FundingOffer", {
    "ID": int,
    "SYMBOL": str,
    "MTS_CREATED": int,
    "MTS_UPDATED": int,
    "AMOUNT": float,
    "AMOUNT_ORIG": float,
    "OFFER_TYPE": str,
    "FLAGS": int,
    "STATUS": str,
    "RATE": float,
    "PERIOD": int,
    "NOTIFY": int,
    "HIDDEN": int,
    "RENEW": int,
})

FundingOffers = List[FundingOffer]

FundingCredit = TypedDict("FundingCredit", {
    "ID": int,
    "SYMBOL": str,
    "SIDE": int,
    "MTS_CREATE": int,
    "MTS_UPDATE": int,
    "AMOUNT": float,
    "FLAGS": int,
    "STATUS": str,
    "RATE": float,
    "PERIOD": int,
    "MTS_OPENING": int,
    "MTS_LAST_PAYOUT": int,
    "NOTIFY": int,
    "HIDDEN": int,
    "RENEW": int,
    "RATE_REAL": float,
    "NO_CLOSE": int,
    "POSITION_PAIR": str
})

FundingCredits = List[FundingCredit]

FundingLoan = TypedDict("FundingLoan", {
    "ID": int,
    "SYMBOL": str,
    "SIDE": int,
    "MTS_CREATE": int,
    "MTS_UPDATE": int,
    "AMOUNT": float,
    "FLAGS": int,
    "STATUS": str,
    "RATE": float,
    "PERIOD": int,
    "MTS_OPENING": int,
    "MTS_LAST_PAYOUT": int,
    "NOTIFY": int,
    "HIDDEN": int,
    "RENEW": int,
    "RATE_REAL": float,
    "NO_CLOSE": int
})

FundingLoans = List[FundingLoan]

Wallet = TypedDict("Wallet", {
    "WALLET_TYPE": str,
    "CURRENCY": str,
    "BALANCE": float,
    "UNSETTLED_INTEREST": float,
    "BALANCE_AVAILABLE": float,
    "DESCRIPTION": str,
    "META": JSON
})

Wallets = List[Wallet]

BalanceInfo = TypedDict("BalanceInfo", {
    "AUM": float,
    "AUM_NET": float
})

#endregion

#region Type hinting for Websocket Authenticated Inputs

class Inputs:
    class Order:
        New = TypedDict("Inputs.Order.New", {
            "gid": Optional[int32],
            "cid": int45,
            "type": str,
            "symbol": str,
            "amount": Union[Decimal, str],
            "price": Union[Decimal, str],
            "lev": int,
            "price_trailing": Union[Decimal, str],
            "price_aux_limit": Union[Decimal, str],
            "price_oco_stop": Union[Decimal, str],
            "flags": int16,
            "tif": Union[datetime, str],
            "meta": JSON
        })

        Update = TypedDict("Inputs.Order.Update", {
            "id": int64,
            "cid": int45,
            "cid_date": str,
            "gid": int32,
            "price": Union[Decimal, str],
            "amount": Union[Decimal, str],
            "lev": int,
            "delta": Union[Decimal, str],
            "price_aux_limit": Union[Decimal, str],
            "price_trailing": Union[Decimal, str],
            "flags": int16,
            "tif": Union[datetime, str]
        })

        Cancel = TypedDict("Inputs.Order.Cancel", {
            "id": int64,
            "cid": int45,
            "cid_date": str
        })

    class Offer:
        New = TypedDict("Inputs.Offer.New", {
            "type": str,
            "symbol": str,
            "amount": Union[Decimal, str],
            "rate": Union[Decimal, str],
            "period": int,
            "flags": int16
        })

        Cancel = TypedDict("Inputs.Offer.Cancel", {
            "id": int
        })
        
#endregion