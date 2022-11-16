from typing import Type, List, Dict, TypedDict, Union, Optional

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for subscription objects

TradingPairsTickerSubscription = TypedDict("TradingPairsTickerSubscription", {
    "chanId": int,
    "symbol": str,
    "pair": str
})

FundingCurrenciesTickerSubscription = TypedDict("FundingCurrenciesTickerSubscription", {
    "chanId": int,
    "symbol": str,
    "currency": str
})

TradingPairsTradesSubscription = TypedDict("TradingPairsTradesSubscription", {
    "chanId": int,
    "symbol": str,
    "pair": str
})

FundingCurrenciesTradesSubscription = TypedDict("FundingCurrenciesTradesSubscription", {
    "chanId": int,
    "symbol": str,
    "currency": str
})

BookSubscription = TypedDict("BookSubscription", {
    "chanId": int,
    "symbol": str,
    "prec": str,
    "freq": str,
    "len": str,
    "subId": int,
    "pair": str
})

CandlesSubscription = TypedDict("CandlesSubscription", {
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

Book = Union[TradingPairBook, FundingCurrencyBook]

Books = Union[TradingPairBooks, FundingCurrencyBooks]

(TradingPairRawBook, FundingCurrencyRawBook) = (
    TypedDict("TradingPairRawBook", { "ORDER_ID": int, "PRICE": float, "AMOUNT": float }),
    TypedDict("FundingCurrencyRawBook", { "OFFER_ID": int, "PERIOD": int, "RATE": float, "AMOUNT": float }),
)

(TradingPairRawBooks, FundingCurrencyRawBooks) = (List[TradingPairRawBook], List[FundingCurrencyRawBook])

RawBook = Union[TradingPairRawBook, FundingCurrencyRawBook]

RawBooks = Union[TradingPairRawBooks, FundingCurrencyRawBooks]

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

Trade = TypedDict("Trade", {
    "ID": int,
    "CID": int,
    "SYMBOL": str,
    "MTS_CREATE": int,
    "ORDER_ID": int,
    "EXEC_AMOUNT": float,
    "EXEC_PRICE": float,
    "ORDER_TYPE": str,
    "ORDER_PRICE": float,
    "MAKER": int,
    "FEE": float,
    "FEE_CURRENCY": str
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