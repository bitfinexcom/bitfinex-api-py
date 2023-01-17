from . import types

from .. labeler import generate_labeler_serializer

from .. notification import _Notification

#region Serializers definition for Websocket Public Channels

TradingPairTicker = generate_labeler_serializer("TradingPairTicker", klass=types.TradingPairTicker, labels=[
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

FundingCurrencyTicker = generate_labeler_serializer("FundingCurrencyTicker", klass=types.FundingCurrencyTicker, labels=[
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

TradingPairTrade = generate_labeler_serializer("TradingPairTrade", klass=types.TradingPairTrade, labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "PRICE" 
])

FundingCurrencyTrade = generate_labeler_serializer("FundingCurrencyTrade", klass=types.FundingCurrencyTrade, labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "RATE", 
    "PERIOD" 
])

TradingPairBook = generate_labeler_serializer("TradingPairBook", klass=types.TradingPairBook, labels=[
    "PRICE", 
    "COUNT", 
    "AMOUNT"
])

FundingCurrencyBook = generate_labeler_serializer("FundingCurrencyBook", klass=types.FundingCurrencyBook, labels=[
    "RATE", 
    "PERIOD", 
    "COUNT", 
    "AMOUNT"
])

TradingPairRawBook = generate_labeler_serializer("TradingPairRawBook", klass=types.TradingPairRawBook, labels=[
    "ORDER_ID", 
    "PRICE", 
    "AMOUNT"
])

FundingCurrencyRawBook = generate_labeler_serializer("FundingCurrencyRawBook", klass=types.FundingCurrencyRawBook, labels=[
    "OFFER_ID", 
    "PERIOD", 
    "RATE", 
    "AMOUNT"
])

Candle = generate_labeler_serializer("Candle", klass=types.Candle, labels=[
    "MTS", 
    "OPEN", 
    "CLOSE", 
    "HIGH", 
    "LOW", 
    "VOLUME"
])

DerivativesStatus = generate_labeler_serializer("DerivativesStatus", klass=types.DerivativesStatus, labels=[
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

Order = generate_labeler_serializer("Order", klass=types.Order, labels=[
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

Position = generate_labeler_serializer("Position", klass=types.Position, labels=[
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

TradeExecuted = generate_labeler_serializer("TradeExecuted", klass=types.TradeExecuted, labels=[
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

TradeExecutionUpdate = generate_labeler_serializer("TradeExecutionUpdate", klass=types.TradeExecutionUpdate, labels=[
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

FundingOffer = generate_labeler_serializer("FundingOffer", klass=types.FundingOffer, labels=[
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

FundingCredit = generate_labeler_serializer("FundingCredit", klass=types.FundingCredit, labels=[
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

FundingLoan = generate_labeler_serializer("FundingLoan", klass=types.FundingLoan, labels=[
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

Wallet = generate_labeler_serializer("Wallet", klass=types.Wallet, labels=[
    "WALLET_TYPE", 
    "CURRENCY", 
    "BALANCE", 
    "UNSETTLED_INTEREST",
    "BALANCE_AVAILABLE",
    "DESCRIPTION",
    "META"
])

BalanceInfo = generate_labeler_serializer("BalanceInfo", klass=types.BalanceInfo, labels=[
    "AUM", 
    "AUM_NET", 
])

#endregion