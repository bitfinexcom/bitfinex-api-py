from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

#region Type hinting for Rest Public Endpoints

PlatformStatus = TypedDict("PlatformStatus", {
    "OPERATIVE": int
})

TradingPairTicker = TypedDict("TradingPairTicker", {
    "SYMBOL": Optional[str],
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
    "SYMBOL": Optional[str],
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

TickerHistory = TypedDict("TickerHistory", {
    "SYMBOL": str,
    "BID": float,
    "ASK": float,
    "MTS": int
})

TickerHistories = List[TickerHistory]

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

Stat = TypedDict("Stat", {
    "MTS": int,
    "VALUE": float
})

Stats = List[Stat]

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
    "KEY": Optional[str],
    "MTS": int,
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

DerivativeStatuses = List[DerivativesStatus]

Liquidation = TypedDict("Liquidation", {
    "POS_ID": int,
    "MTS": int,
    "SYMBOL": str,
    "AMOUNT": float,
    "BASE_PRICE": float,
    "IS_MATCH": int,
    "IS_MARKET_SOLD": int,
    "PRICE_ACQUIRED": float
})

Liquidations = List[Liquidation]

Leaderboard = TypedDict("Leaderboard", {
    "MTS": int,
    "USERNAME": str,
    "RANKING": int,
    "VALUE": float,
    "TWITTER_HANDLE": Optional[str]
})

Leaderboards = List[Leaderboard]

FundingStat = TypedDict("FundingStat", {
    "TIMESTAMP": int,
    "FRR": float,
    "AVG_PERIOD": float,
    "FUNDING_AMOUNT": float,
    "FUNDING_AMOUNT_USED": float,
    "FUNDING_BELOW_THRESHOLD": float
})

FundingStats = List[FundingStat]

#endregion