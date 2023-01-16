from . import types

from .. labeler import _Serializer

from .. notification import _Notification

#region Serializers definition for Websocket Public Channels

TradingPairTicker = _Serializer[types.TradingPairTicker]("TradingPairTicker", labels=[
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

FundingCurrencyTicker = _Serializer[types.FundingCurrencyTicker]("FundingCurrencyTicker", labels=[
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
    "LOW"
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FRR_AMOUNT_AVAILABLE"
])

TradingPairTrade = _Serializer[types.TradingPairTrade]("TradingPairTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "PRICE" 
])

FundingCurrencyTrade = _Serializer[types.FundingCurrencyTrade]("FundingCurrencyTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "RATE", 
    "PERIOD" 
])

TradingPairBook = _Serializer[types.TradingPairBook]("TradingPairBook", labels=[
    "PRICE", 
    "COUNT", 
    "AMOUNT"
])

FundingCurrencyBook = _Serializer[types.FundingCurrencyBook]("FundingCurrencyBook", labels=[
    "RATE", 
    "PERIOD", 
    "COUNT", 
    "AMOUNT"
])

TradingPairRawBook = _Serializer[types.TradingPairRawBook]("TradingPairRawBook", labels=[
    "ORDER_ID", 
    "PRICE", 
    "AMOUNT"
])

FundingCurrencyRawBook = _Serializer[types.FundingCurrencyRawBook]("FundingCurrencyRawBook", labels=[
    "OFFER_ID", 
    "PERIOD", 
    "RATE", 
    "AMOUNT"
])

Candle = _Serializer[types.Candle]("Candle", labels=[
    "MTS", 
    "OPEN", 
    "CLOSE", 
    "HIGH", 
    "LOW", 
    "VOLUME"
])

DerivativesStatus = _Serializer[types.DerivativesStatus]("DerivativesStatus", labels=[
    "TIME_MS",
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
    "CURRENT_FUNDING"
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

#endregion

#region Serializers definition for Websocket Authenticated Channels

Order = _Serializer[types.Order]("Order", labels=[
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

Position = _Serializer[types.Position]("Position", labels=[
    "SYMBOL", 
    "STATUS", 
    "AMOUNT", 
    "BASE_PRICE", 
    "MARGIN_FUNDING", 
    "MARGIN_FUNDING_TYPE",
    "PL",
    "PL_PERC",
    "PRICE_LIQ",
    "LEVERAGE",
    "FLAG",
    "POSITION_ID",
    "MTS_CREATE",
    "MTS_UPDATE",
    "_PLACEHOLDER",
    "TYPE",
    "_PLACEHOLDER",
    "COLLATERAL",
    "COLLATERAL_MIN",
    "META"
])

TradeExecuted = _Serializer[types.TradeExecuted]("TradeExecuted", labels=[
    "ID", 
    "SYMBOL", 
    "MTS_CREATE",
    "ORDER_ID", 
    "EXEC_AMOUNT", 
    "EXEC_PRICE", 
    "ORDER_TYPE", 
    "ORDER_PRICE", 
    "MAKER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "CID"
])

TradeExecutionUpdate = _Serializer[types.TradeExecutionUpdate]("TradeExecutionUpdate", labels=[
    "ID", 
    "SYMBOL", 
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

FundingOffer = _Serializer[types.FundingOffer]("FundingOffer", labels=[
    "ID",
    "SYMBOL",
    "MTS_CREATED",
    "MTS_UPDATED",
    "AMOUNT",
    "AMOUNT_ORIG",
    "OFFER_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "_PLACEHOLDER"
])

FundingCredit = _Serializer[types.FundingCredit]("FundingCredit", labels=[
    "ID",
    "SYMBOL",
    "SIDE",
    "MTS_CREATE",
    "MTS_UPDATE",
    "AMOUNT",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "MTS_OPENING",
    "MTS_LAST_PAYOUT",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "RATE_REAL",
    "NO_CLOSE",
    "POSITION_PAIR"
])

FundingLoan = _Serializer[types.FundingLoan]("FundingLoan", labels=[
    "ID",
    "SYMBOL",
    "SIDE",
    "MTS_CREATE",
    "MTS_UPDATE",
    "AMOUNT",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "MTS_OPENING",
    "MTS_LAST_PAYOUT",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "RATE_REAL",
    "NO_CLOSE"
])

Wallet = _Serializer[types.Wallet]("Wallet", labels=[
    "WALLET_TYPE", 
    "CURRENCY", 
    "BALANCE", 
    "UNSETTLED_INTEREST",
    "BALANCE_AVAILABLE",
    "DESCRIPTION",
    "META"
])

BalanceInfo = _Serializer[types.BalanceInfo]("BalanceInfo", labels=[
    "AUM", 
    "AUM_NET", 
])

#endregion