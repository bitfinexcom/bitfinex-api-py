from . import types

from .. labeler import generate_labeler_serializer, generate_recursive_serializer

from .. notification import _Notification

#region Serializers definition for Rest Public Endpoints

PlatformStatus = generate_labeler_serializer("PlatformStatus", klass=types.PlatformStatus, labels=[
    "STATUS"
])

TradingPairTicker = generate_labeler_serializer("TradingPairTicker", klass=types.TradingPairTicker, labels=[
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

FundingCurrencyTicker = generate_labeler_serializer("FundingCurrencyTicker", klass=types.FundingCurrencyTicker, labels=[
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

TickersHistory = generate_labeler_serializer("TickersHistory", klass=types.TickersHistory, labels=[
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

Statistic = generate_labeler_serializer("Statistic", klass=types.Statistic, labels=[
    "MTS",
    "VALUE"
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

Liquidation = generate_labeler_serializer("Liquidation", klass=types.Liquidation, labels=[
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

Leaderboard = generate_labeler_serializer("Leaderboard", klass=types.Leaderboard, labels=[
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

FundingStatistic = generate_labeler_serializer("FundingStatistic", klass=types.FundingStatistic, labels=[
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

PulseProfile = generate_labeler_serializer("PulseProfile", klass=types.PulseProfile, labels=[
    "PUID",
    "MTS",
    "_PLACEHOLDER",
    "NICKNAME",
    "_PLACEHOLDER",
    "PICTURE",
    "TEXT",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "TWITTER_HANDLE",
    "_PLACEHOLDER",
    "FOLLOWERS",
    "FOLLOWING",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "TIPPING_STATUS"
])

PulseMessage = generate_recursive_serializer("PulseMessage", klass=types.PulseMessage, serializers={ "PROFILE": PulseProfile }, labels=[
    "PID",
    "MTS",
    "_PLACEHOLDER",
    "PUID",
    "_PLACEHOLDER",
    "TITLE",
    "CONTENT",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "IS_PIN",
    "IS_PUBLIC",
    "COMMENTS_DISABLED",
    "TAGS", 
    "ATTACHMENTS",
    "META",
    "LIKES",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "PROFILE",
    "COMMENTS",
    "_PLACEHOLDER",
    "_PLACEHOLDER"
])

TradingMarketAveragePrice = generate_labeler_serializer("TradingMarketAveragePrice", klass=types.TradingMarketAveragePrice, labels=[
    "PRICE_AVG",
    "AMOUNT"
])

FundingMarketAveragePrice = generate_labeler_serializer("FundingMarketAveragePrice", klass=types.FundingMarketAveragePrice, labels=[
    "RATE_AVG",
    "AMOUNT"
])

FxRate = generate_labeler_serializer("FxRate", klass=types.FxRate, labels=[
    "CURRENT_RATE"
])

#endregion

#region Serializers definition for Rest Authenticated Endpoints

Wallet = generate_labeler_serializer("Wallet", klass=types.Wallet, labels=[
    "WALLET_TYPE", 
    "CURRENCY", 
    "BALANCE", 
    "UNSETTLED_INTEREST",
    "AVAILABLE_BALANCE",
    "LAST_CHANGE",
    "TRADE_DETAILS"
])

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
    "_PLACEHOLDER",
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
    "OFFER_STATUS",
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

Trade = generate_labeler_serializer("Trade", klass=types.Trade, labels=[
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

OrderTrade = generate_labeler_serializer("OrderTrade", klass=types.OrderTrade, labels=[
    "ID",
    "PAIR",
    "MTS_CREATE",
    "ORDER_ID",
    "EXEC_AMOUNT",
    "EXEC_PRICE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "MAKER",
    "FEE",
    "FEE_CURRENCY",
    "CID"
])

Ledger = generate_labeler_serializer("Ledger", klass=types.Ledger, labels=[
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

FundingCredit = generate_labeler_serializer("FundingCredit", klass=types.FundingCredit, labels=[
    "ID",
    "SYMBOL",
    "SIDE",
    "MTS_CREATE",
    "MTS_UPDATE",
    "AMOUNT",
    "FLAGS",
    "STATUS",
    "RATE_TYPE",
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
    "_PLACEHOLDER",
    "NO_CLOSE",
    "POSITION_PAIR"
])

Transfer = generate_labeler_serializer("Transfer", klass=types.Transfer, labels=[
    "MTS",
    "WALLET_FROM",
    "WALLET_TO",
    "_PLACEHOLDER",
    "CURRENCY",
    "CURRENCY_TO",
    "_PLACEHOLDER",
    "AMOUNT"
])

Withdrawal = generate_labeler_serializer("Withdrawal", klass=types.Withdrawal, labels=[
    "WITHDRAWAL_ID",
    "_PLACEHOLDER",
    "METHOD",
    "PAYMENT_ID",
    "WALLET",
    "AMOUNT",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "WITHDRAWAL_FEE"
])

DepositAddress = generate_labeler_serializer("DepositAddress", klass=types.DepositAddress, labels=[
    "_PLACEHOLDER",
    "METHOD",
    "CURRENCY_CODE",
    "_PLACEHOLDER",
    "ADDRESS",
    "POOL_ADDRESS"
])

Invoice = generate_labeler_serializer("Invoice", klass=types.Invoice, labels=[
    "INVOICE_HASH",
    "INVOICE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "AMOUNT"
])

Movement = generate_labeler_serializer("Movement", klass=types.Movement, labels=[
    "ID",
    "CURRENCY",
    "CURRENCY_NAME",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "MTS_STARTED",
    "MTS_UPDATED",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "AMOUNT",
    "FEES",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "DESTINATION_ADDRESS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "TRANSACTION_ID",
    "WITHDRAW_TRANSACTION_NOTE"
])

SymbolMarginInfo = generate_labeler_serializer("SymbolMarginInfo", klass=types.SymbolMarginInfo, labels=[
    "SYMBOL",
    "TRADABLE_BALANCE",
    "GROSS_BALANCE",
    "BUY",
    "SELL"
])

BaseMarginInfo = generate_labeler_serializer("BaseMarginInfo", klass=types.BaseMarginInfo, labels=[
    "USER_PL",
    "USER_SWAPS",
    "MARGIN_BALANCE",
    "MARGIN_NET",
    "MARGIN_MIN"
])

Claim = generate_labeler_serializer("Claim", klass=types.Claim, labels=[
    "SYMBOL",
    "POSITION_STATUS",
    "AMOUNT",
    "BASE_PRICE",
    "MARGIN_FUNDING",
    "MARGIN_FUNDING_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "POSITION_ID",
    "MTS_CREATE",
    "MTS_UPDATE",
    "_PLACEHOLDER",
    "POS_TYPE",
    "_PLACEHOLDER",
    "COLLATERAL",
    "MIN_COLLATERAL",
    "META"
])

IncreaseInfo = generate_labeler_serializer("IncreaseInfo", klass=types.IncreaseInfo, labels=[
    "MAX_POS",
    "CURRENT_POS",
    "BASE_CURRENCY_BALANCE",
    "TRADABLE_BALANCE_QUOTE_CURRENCY",
    "TRADABLE_BALANCE_QUOTE_TOTAL",
    "TRADABLE_BALANCE_BASE_CURRENCY",
    "TRADABLE_BALANCE_BASE_TOTAL",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FUNDING_AVAIL",
    "FUNDING_VALUE",
    "FUNDING_REQUIRED",
    "FUNDING_VALUE_CURRENCY",
    "FUNDING_REQUIRED_CURRENCY"
])

Increase = generate_labeler_serializer("Increase", klass=types.Increase, labels=[
    "SYMBOL",
    "_PLACEHOLDER",
    "AMOUNT",
    "BASE_PRICE"
])

PositionHistory = generate_labeler_serializer("PositionHistory", klass=types.PositionHistory, labels=[
    "SYMBOL",
    "STATUS",
    "AMOUNT",
    "BASE_PRICE",
    "FUNDING",
    "FUNDING_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "POSITION_ID",
    "MTS_CREATE",
    "MTS_UPDATE"
])

PositionSnapshot = generate_labeler_serializer("PositionSnapshot", klass=types.PositionSnapshot, labels=[
    "SYMBOL",
    "STATUS",
    "AMOUNT",
    "BASE_PRICE",
    "FUNDING",
    "FUNDING_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "POSITION_ID",
    "MTS_CREATE",
    "MTS_UPDATE"
])

PositionAudit = generate_labeler_serializer("PositionAudit", klass=types.PositionAudit, labels=[
    "SYMBOL",
    "STATUS",
    "AMOUNT",
    "BASE_PRICE",
    "FUNDING",
    "FUNDING_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
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

DerivativePositionCollateral = generate_labeler_serializer("DerivativePositionCollateral", klass=types.DerivativePositionCollateral, labels=[
    "STATUS"
])

DerivativePositionCollateralLimits = generate_labeler_serializer("DerivativePositionCollateralLimits", klass=types.DerivativePositionCollateralLimits, labels=[
    "MIN_COLLATERAL",
    "MAX_COLLATERAL"
])

#endregion