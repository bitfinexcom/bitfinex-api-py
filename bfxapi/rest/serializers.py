from . import typings

from .. labeler import _Serializer

from .. notification import _Notification

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

TickersHistory = _Serializer[typings.TickersHistory]("TickersHistory", labels=[
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

TradingPairBook = _Serializer[typings.TradingPairBook]("TradingPairBook", labels=[
    "PRICE", 
    "COUNT", 
    "AMOUNT"
])

FundingCurrencyBook = _Serializer[typings.FundingCurrencyBook]("FundingCurrencyBook", labels=[
    "RATE", 
    "PERIOD", 
    "COUNT", 
    "AMOUNT"
])

TradingPairRawBook = _Serializer[typings.TradingPairRawBook]("TradingPairRawBook", labels=[
    "ORDER_ID", 
    "PRICE", 
    "AMOUNT"
])

FundingCurrencyRawBook = _Serializer[typings.FundingCurrencyRawBook]("FundingCurrencyRawBook", labels=[
    "OFFER_ID", 
    "PERIOD", 
    "RATE", 
    "AMOUNT"
])

Statistic = _Serializer[typings.Statistic]("Statistic", labels=[
    "MTS",
    "VALUE"
])

Candle = _Serializer[typings.Candle]("Candle", labels=[
    "MTS",
    "OPEN",
    "CLOSE",
    "HIGH",
    "LOW",
    "VOLUME"
])

DerivativesStatus = _Serializer[typings.DerivativesStatus]("DerivativesStatus", labels=[
    "KEY",
    "MTS",
    "_PLACEHOLDER", 
    "DERIV_PRICE",
    "SPOT_PRICE",
    "_PLACEHOLDER",
    "INSURANCE_FUND_BALANCE",
    "_PLACEHOLDER",
    "NEXT_FUNDING_EVT_TIMESTAMP_MS",
    "NEXT_FUNDING_ACCRUED",
    "NEXT_FUNDING_STEP",
    "_PLACEHOLDER",
    "CURRENT_FUNDING",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "MARK_PRICE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "OPEN_INTEREST",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "CLAMP_MIN",
    "CLAMP_MAX"
])

Liquidation = _Serializer[typings.Liquidation]("Liquidation", labels=[
    "_PLACEHOLDER",
    "POS_ID",
    "MTS",
    "_PLACEHOLDER",
    "SYMBOL",
    "AMOUNT",
    "BASE_PRICE",
    "_PLACEHOLDER",
    "IS_MATCH",
    "IS_MARKET_SOLD",
    "_PLACEHOLDER",
    "PRICE_ACQUIRED"
])

Leaderboard = _Serializer[typings.Leaderboard]("Leaderboard", labels=[
    "MTS",
    "_PLACEHOLDER",
    "USERNAME",
    "RANKING",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "VALUE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "TWITTER_HANDLE"
])

FundingStatistic = _Serializer[typings.FundingStatistic]("FundingStatistic", labels=[
    "TIMESTAMP",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FRR",
    "AVG_PERIOD",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FUNDING_AMOUNT",
    "FUNDING_AMOUNT_USED",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FUNDING_BELOW_THRESHOLD"
])

#endregion

#region Serializers definition for Rest Authenticated Endpoints

Wallet = _Serializer[typings.Wallet]("Wallet", labels=[
    "WALLET_TYPE", 
    "CURRENCY", 
    "BALANCE", 
    "UNSETTLED_INTEREST",
    "AVAILABLE_BALANCE",
    "LAST_CHANGE",
    "TRADE_DETAILS"
])

Order = _Serializer[typings.Order]("Order", labels=[
    "ID",
    "GID",
    "CID",
    "SYMBOL",
    "MTS_CREATE", 
    "MTS_UPDATE", 
    "AMOUNT", 
    "AMOUNT_ORIG", 
    "ORDER_TYPE",
    "TYPE_PREV",
    "MTS_TIF",
    "_PLACEHOLDER",
    "FLAGS",
    "ORDER_STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "PRICE",
    "PRICE_AVG",
    "PRICE_TRAILING",
    "PRICE_AUX_LIMIT",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "NOTIFY",
    "HIDDEN", 
    "PLACED_ID",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "ROUTING",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "META"
])

Trade = _Serializer[typings.Trade]("Trade", labels=[
    "ID", 
    "PAIR", 
    "MTS_CREATE", 
    "ORDER_ID", 
    "EXEC_AMOUNT", 
    "EXEC_PRICE", 
    "ORDER_TYPE", 
    "ORDER_PRICE", 
    "MAKER", 
    "FEE", 
    "FEE_CURRENCY",
    "CID"
])

Ledger = _Serializer[typings.Ledger]("Ledger", labels=[
    "ID",
    "CURRENCY",
    "_PLACEHOLDER",
    "MTS",
    "_PLACEHOLDER",
    "AMOUNT",
    "BALANCE",
    "_PLACEHOLDER",
    "DESCRIPTION"
])

#endregion