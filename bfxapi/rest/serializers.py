from . import types

from .. labeler import generate_labeler_serializer, generate_recursive_serializer

from .. notification import _Notification

#region Serializers definition for Rest Public Endpoints

PlatformStatus = generate_labeler_serializer("PlatformStatus", klass=types.PlatformStatus, labels=[
    "status"
])

TradingPairTicker = generate_labeler_serializer("TradingPairTicker", klass=types.TradingPairTicker, labels=[
    "symbol",
    "bid",
    "bid_size",
    "ask",
    "ask_size",
    "daily_change",
    "daily_change_relative",
    "last_price",
    "volume",
    "high",
    "low"
])

FundingCurrencyTicker = generate_labeler_serializer("FundingCurrencyTicker", klass=types.FundingCurrencyTicker, labels=[
    "symbol",
    "frr",
    "bid",
    "bid_period",
    "bid_size",
    "ask",
    "ask_period",
    "ask_size",
    "daily_change",
    "daily_change_relative",
    "last_price",
    "volume",
    "high",
    "low",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "frr_amount_available"
])

TickersHistory = generate_labeler_serializer("TickersHistory", klass=types.TickersHistory, labels=[
    "symbol",
    "bid",
    "_PLACEHOLDER",
    "ask",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "mts"
])

TradingPairTrade = generate_labeler_serializer("TradingPairTrade", klass=types.TradingPairTrade, labels=[ 
    "id", 
    "mts", 
    "amount", 
    "price" 
])

FundingCurrencyTrade = generate_labeler_serializer("FundingCurrencyTrade", klass=types.FundingCurrencyTrade, labels=[ 
    "id", 
    "mts", 
    "amount", 
    "rate", 
    "period" 
])

TradingPairBook = generate_labeler_serializer("TradingPairBook", klass=types.TradingPairBook, labels=[
    "price", 
    "count", 
    "amount"
])

FundingCurrencyBook = generate_labeler_serializer("FundingCurrencyBook", klass=types.FundingCurrencyBook, labels=[
    "rate", 
    "period", 
    "count", 
    "amount"
])

TradingPairRawBook = generate_labeler_serializer("TradingPairRawBook", klass=types.TradingPairRawBook, labels=[
    "order_id", 
    "price", 
    "amount"
])

FundingCurrencyRawBook = generate_labeler_serializer("FundingCurrencyRawBook", klass=types.FundingCurrencyRawBook, labels=[
    "offer_id", 
    "period", 
    "rate", 
    "amount"
])

Statistic = generate_labeler_serializer("Statistic", klass=types.Statistic, labels=[
    "mts",
    "value"
])

Candle = generate_labeler_serializer("Candle", klass=types.Candle, labels=[
    "mts",
    "open",
    "close",
    "high",
    "low",
    "volume"
])

DerivativesStatus = generate_labeler_serializer("DerivativesStatus", klass=types.DerivativesStatus, labels=[
    "key",
    "mts",
    "_PLACEHOLDER", 
    "deriv_price",
    "spot_price",
    "_PLACEHOLDER",
    "insurance_fund_balance",
    "_PLACEHOLDER",
    "next_funding_evt_timestamp_ms",
    "next_funding_accrued",
    "next_funding_step",
    "_PLACEHOLDER",
    "current_funding",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "mark_price",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "open_interest",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "clamp_min",
    "clamp_max"
])

Liquidation = generate_labeler_serializer("Liquidation", klass=types.Liquidation, labels=[
    "_PLACEHOLDER",
    "pos_id",
    "mts",
    "_PLACEHOLDER",
    "symbol",
    "amount",
    "base_price",
    "_PLACEHOLDER",
    "is_match",
    "is_market_sold",
    "_PLACEHOLDER",
    "price_acquired"
])

Leaderboard = generate_labeler_serializer("Leaderboard", klass=types.Leaderboard, labels=[
    "mts",
    "_PLACEHOLDER",
    "username",
    "ranking",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "value",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "twitter_handle"
])

FundingStatistic = generate_labeler_serializer("FundingStatistic", klass=types.FundingStatistic, labels=[
    "timestamp",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "frr",
    "avg_period",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "funding_amount",
    "funding_amount_used",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "funding_below_threshold"
])

PulseProfile = generate_labeler_serializer("PulseProfile", klass=types.PulseProfile, labels=[
    "puid",
    "mts",
    "_PLACEHOLDER",
    "nickname",
    "_PLACEHOLDER",
    "picture",
    "text",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "twitter_handle",
    "_PLACEHOLDER",
    "followers",
    "following",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "tipping_status"
])

PulseMessage = generate_recursive_serializer("PulseMessage", klass=types.PulseMessage, serializers={ "profile": PulseProfile }, labels=[
    "pid",
    "mts",
    "_PLACEHOLDER",
    "puid",
    "_PLACEHOLDER",
    "title",
    "content",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "is_pin",
    "is_public",
    "comments_disabled",
    "tags", 
    "attachments",
    "meta",
    "likes",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "profile",
    "comments",
    "_PLACEHOLDER",
    "_PLACEHOLDER"
])

TradingMarketAveragePrice = generate_labeler_serializer("TradingMarketAveragePrice", klass=types.TradingMarketAveragePrice, labels=[
    "price_avg",
    "amount"
])

FundingMarketAveragePrice = generate_labeler_serializer("FundingMarketAveragePrice", klass=types.FundingMarketAveragePrice, labels=[
    "rate_avg",
    "amount"
])

FxRate = generate_labeler_serializer("FxRate", klass=types.FxRate, labels=[
    "current_rate"
])

#endregion

#region Serializers definition for Rest Authenticated Endpoints

Wallet = generate_labeler_serializer("Wallet", klass=types.Wallet, labels=[
    "wallet_type", 
    "currency", 
    "balance", 
    "unsettled_interest",
    "available_balance",
    "last_change",
    "trade_details"
])

Order = generate_labeler_serializer("Order", klass=types.Order, labels=[
    "id",
    "gid",
    "cid",
    "symbol",
    "mts_create", 
    "mts_update", 
    "amount", 
    "amount_orig", 
    "order_type",
    "type_prev",
    "mts_tif",
    "_PLACEHOLDER",
    "flags",
    "order_status",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "price",
    "price_avg",
    "price_trailing",
    "price_aux_limit",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "notify",
    "hidden", 
    "placed_id",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "routing",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "meta"
])

Position = generate_labeler_serializer("Position", klass=types.Position, labels=[
    "symbol", 
    "status", 
    "amount", 
    "base_price", 
    "margin_funding", 
    "margin_funding_type",
    "pl",
    "pl_perc",
    "price_liq",
    "leverage",
    "_PLACEHOLDER",
    "position_id",
    "mts_create",
    "mts_update",
    "_PLACEHOLDER",
    "type",
    "_PLACEHOLDER",
    "collateral",
    "collateral_min",
    "meta"
])

FundingOffer = generate_labeler_serializer("FundingOffer", klass=types.FundingOffer, labels=[
    "id",
    "symbol",
    "mts_create",
    "mts_update",
    "amount",
    "amount_orig",
    "offer_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "flags",
    "offer_status",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "rate",
    "period",
    "notify",
    "hidden",
    "_PLACEHOLDER",
    "renew",
    "_PLACEHOLDER"
])

Trade = generate_labeler_serializer("Trade", klass=types.Trade, labels=[
    "id", 
    "pair", 
    "mts_create", 
    "order_id", 
    "exec_amount", 
    "exec_price", 
    "order_type", 
    "order_price", 
    "maker", 
    "fee", 
    "fee_currency",
    "cid"
])

OrderTrade = generate_labeler_serializer("OrderTrade", klass=types.OrderTrade, labels=[
    "id",
    "pair",
    "mts_create",
    "order_id",
    "exec_amount",
    "exec_price",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "maker",
    "fee",
    "fee_currency",
    "cid"
])

Ledger = generate_labeler_serializer("Ledger", klass=types.Ledger, labels=[
    "id",
    "currency",
    "_PLACEHOLDER",
    "mts",
    "_PLACEHOLDER",
    "amount",
    "balance",
    "_PLACEHOLDER",
    "description"
])

FundingLoan = generate_labeler_serializer("FundingLoan", klass=types.FundingLoan, labels=[
    "id",
    "symbol",
    "side",
    "mts_create",
    "mts_update",
    "amount",
    "flags",
    "status",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "rate",
    "period",
    "mts_opening",
    "mts_last_payout",
    "notify",
    "hidden",
    "_PLACEHOLDER",
    "renew",
    "rate_real",
    "no_close"
])

FundingCredit = generate_labeler_serializer("FundingCredit", klass=types.FundingCredit, labels=[
    "id",
    "symbol",
    "side",
    "mts_create",
    "mts_update",
    "amount",
    "flags",
    "status",
    "rate_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "rate",
    "period",
    "mts_opening",
    "mts_last_payout",
    "notify",
    "hidden",
    "_PLACEHOLDER",
    "renew",
    "_PLACEHOLDER",
    "no_close",
    "position_pair"
])

FundingAutoRenew = generate_labeler_serializer("FundingAutoRenew", klass=types.FundingAutoRenew, labels=[
    "currency",
    "period",
    "rate",
    "threshold"
])

Transfer = generate_labeler_serializer("Transfer", klass=types.Transfer, labels=[
    "mts",
    "wallet_from",
    "wallet_to",
    "_PLACEHOLDER",
    "currency",
    "currency_to",
    "_PLACEHOLDER",
    "amount"
])

Withdrawal = generate_labeler_serializer("Withdrawal", klass=types.Withdrawal, labels=[
    "withdrawal_id",
    "_PLACEHOLDER",
    "method",
    "payment_id",
    "wallet",
    "amount",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "withdrawal_fee"
])

DepositAddress = generate_labeler_serializer("DepositAddress", klass=types.DepositAddress, labels=[
    "_PLACEHOLDER",
    "method",
    "currency_code",
    "_PLACEHOLDER",
    "address",
    "pool_address"
])

Invoice = generate_labeler_serializer("Invoice", klass=types.Invoice, labels=[
    "invoice_hash",
    "invoice",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "amount"
])

Movement = generate_labeler_serializer("Movement", klass=types.Movement, labels=[
    "id",
    "currency",
    "currency_name",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "mts_start",
    "mts_update",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "status",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "amount",
    "fees",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "destination_address",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "transaction_id",
    "withdraw_transaction_note"
])

SymbolMarginInfo = generate_labeler_serializer("SymbolMarginInfo", klass=types.SymbolMarginInfo, labels=[
    "symbol",
    "tradable_balance",
    "gross_balance",
    "buy",
    "sell"
])

BaseMarginInfo = generate_labeler_serializer("BaseMarginInfo", klass=types.BaseMarginInfo, labels=[
    "user_pl",
    "user_swaps",
    "margin_balance",
    "margin_net",
    "margin_min"
])

Claim = generate_labeler_serializer("Claim", klass=types.Claim, labels=[
    "symbol",
    "position_status",
    "amount",
    "base_price",
    "margin_funding",
    "margin_funding_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "position_id",
    "mts_create",
    "mts_update",
    "_PLACEHOLDER",
    "pos_type",
    "_PLACEHOLDER",
    "collateral",
    "min_collateral",
    "meta"
])

IncreaseInfo = generate_labeler_serializer("IncreaseInfo", klass=types.IncreaseInfo, labels=[
    "max_pos",
    "current_pos",
    "base_currency_balance",
    "tradable_balance_quote_currency",
    "tradable_balance_quote_total",
    "tradable_balance_base_currency",
    "tradable_balance_base_total",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "funding_avail",
    "funding_value",
    "funding_required",
    "funding_value_currency",
    "funding_required_currency"
])

Increase = generate_labeler_serializer("Increase", klass=types.Increase, labels=[
    "symbol",
    "_PLACEHOLDER",
    "amount",
    "base_price"
])

PositionHistory = generate_labeler_serializer("PositionHistory", klass=types.PositionHistory, labels=[
    "symbol",
    "status",
    "amount",
    "base_price",
    "funding",
    "funding_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "position_id",
    "mts_create",
    "mts_update"
])

PositionSnapshot = generate_labeler_serializer("PositionSnapshot", klass=types.PositionSnapshot, labels=[
    "symbol",
    "status",
    "amount",
    "base_price",
    "funding",
    "funding_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "position_id",
    "mts_create",
    "mts_update"
])

PositionAudit = generate_labeler_serializer("PositionAudit", klass=types.PositionAudit, labels=[
    "symbol",
    "status",
    "amount",
    "base_price",
    "funding",
    "funding_type",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "position_id",
    "mts_create",
    "mts_update",
    "_PLACEHOLDER",
    "type",
    "_PLACEHOLDER",
    "collateral",
    "collateral_min",
    "meta"
])

DerivativePositionCollateral = generate_labeler_serializer("DerivativePositionCollateral", klass=types.DerivativePositionCollateral, labels=[
    "status"
])

DerivativePositionCollateralLimits = generate_labeler_serializer("DerivativePositionCollateralLimits", klass=types.DerivativePositionCollateralLimits, labels=[
    "min_collateral",
    "max_collateral"
])

#endregion