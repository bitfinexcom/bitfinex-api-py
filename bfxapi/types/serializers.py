from . import dataclasses
from .labeler import (  # noqa: F401
    _Serializer,
    generate_labeler_serializer,
    generate_recursive_serializer,
)
from .notification import _Notification  # noqa: F401

__serializers__ = [
    "PlatformStatus",
    "TradingPairTicker",
    "FundingCurrencyTicker",
    "TickersHistory",
    "TradingPairTrade",
    "FundingCurrencyTrade",
    "TradingPairBook",
    "FundingCurrencyBook",
    "TradingPairRawBook",
    "FundingCurrencyRawBook",
    "Statistic",
    "Candle",
    "DerivativesStatus",
    "Liquidation",
    "Leaderboard",
    "FundingStatistic",
    "PulseProfile",
    "PulseMessage",
    "TradingMarketAveragePrice",
    "FundingMarketAveragePrice",
    "FxRate",
    "UserInfo",
    "LoginHistory",
    "BalanceAvailable",
    "Order",
    "Position",
    "Trade",
    "FundingTrade",
    "OrderTrade",
    "Ledger",
    "FundingOffer",
    "FundingCredit",
    "FundingLoan",
    "FundingAutoRenew",
    "FundingInfo",
    "Wallet",
    "Transfer",
    "Withdrawal",
    "DepositAddress",
    "LightningNetworkInvoice",
    "Movement",
    "SymbolMarginInfo",
    "BaseMarginInfo",
    "PositionClaim",
    "PositionIncreaseInfo",
    "PositionIncrease",
    "PositionHistory",
    "PositionSnapshot",
    "PositionAudit",
    "DerivativePositionCollateral",
    "DerivativePositionCollateralLimits",
]

# region Serializer definitions for types of public use

PlatformStatus = generate_labeler_serializer(
    name="PlatformStatus", klass=dataclasses.PlatformStatus, labels=["status"]
)

TradingPairTicker = generate_labeler_serializer(
    name="TradingPairTicker",
    klass=dataclasses.TradingPairTicker,
    labels=[
        "bid",
        "bid_size",
        "ask",
        "ask_size",
        "daily_change",
        "daily_change_relative",
        "last_price",
        "volume",
        "high",
        "low",
    ],
)

FundingCurrencyTicker = generate_labeler_serializer(
    name="FundingCurrencyTicker",
    klass=dataclasses.FundingCurrencyTicker,
    labels=[
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
        "frr_amount_available",
    ],
)

TickersHistory = generate_labeler_serializer(
    name="TickersHistory",
    klass=dataclasses.TickersHistory,
    labels=[
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
        "mts",
    ],
)

TradingPairTrade = generate_labeler_serializer(
    name="TradingPairTrade",
    klass=dataclasses.TradingPairTrade,
    labels=["id", "mts", "amount", "price"],
)

FundingCurrencyTrade = generate_labeler_serializer(
    name="FundingCurrencyTrade",
    klass=dataclasses.FundingCurrencyTrade,
    labels=["id", "mts", "amount", "rate", "period"],
)

TradingPairBook = generate_labeler_serializer(
    name="TradingPairBook",
    klass=dataclasses.TradingPairBook,
    labels=["price", "count", "amount"],
)

FundingCurrencyBook = generate_labeler_serializer(
    name="FundingCurrencyBook",
    klass=dataclasses.FundingCurrencyBook,
    labels=["rate", "period", "count", "amount"],
)

TradingPairRawBook = generate_labeler_serializer(
    name="TradingPairRawBook",
    klass=dataclasses.TradingPairRawBook,
    labels=["order_id", "price", "amount"],
)

FundingCurrencyRawBook = generate_labeler_serializer(
    name="FundingCurrencyRawBook",
    klass=dataclasses.FundingCurrencyRawBook,
    labels=["offer_id", "period", "rate", "amount"],
)

Statistic = generate_labeler_serializer(
    name="Statistic", klass=dataclasses.Statistic, labels=["mts", "value"]
)

Candle = generate_labeler_serializer(
    name="Candle",
    klass=dataclasses.Candle,
    labels=["mts", "open", "close", "high", "low", "volume"],
)

DerivativesStatus = generate_labeler_serializer(
    name="DerivativesStatus",
    klass=dataclasses.DerivativesStatus,
    labels=[
        "mts",
        "_PLACEHOLDER",
        "deriv_price",
        "spot_price",
        "_PLACEHOLDER",
        "insurance_fund_balance",
        "_PLACEHOLDER",
        "next_funding_evt_mts",
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
        "clamp_max",
    ],
)

Liquidation = generate_labeler_serializer(
    name="Liquidation",
    klass=dataclasses.Liquidation,
    labels=[
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
        "liquidation_price",
    ],
)

Leaderboard = generate_labeler_serializer(
    name="Leaderboard",
    klass=dataclasses.Leaderboard,
    labels=[
        "mts",
        "_PLACEHOLDER",
        "username",
        "ranking",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "value",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "twitter_handle",
    ],
)

FundingStatistic = generate_labeler_serializer(
    name="FundingStatistic",
    klass=dataclasses.FundingStatistic,
    labels=[
        "mts",
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
        "funding_below_threshold",
    ],
)

PulseProfile = generate_labeler_serializer(
    name="PulseProfile",
    klass=dataclasses.PulseProfile,
    labels=[
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
        "tipping_status",
    ],
)

PulseMessage = generate_recursive_serializer(
    name="PulseMessage",
    klass=dataclasses.PulseMessage,
    serializers={"profile": PulseProfile},
    labels=[
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
        "_PLACEHOLDER",
    ],
)

TradingMarketAveragePrice = generate_labeler_serializer(
    name="TradingMarketAveragePrice",
    klass=dataclasses.TradingMarketAveragePrice,
    labels=["price_avg", "amount"],
)

FundingMarketAveragePrice = generate_labeler_serializer(
    name="FundingMarketAveragePrice",
    klass=dataclasses.FundingMarketAveragePrice,
    labels=["rate_avg", "amount"],
)

FxRate = generate_labeler_serializer(
    name="FxRate", klass=dataclasses.FxRate, labels=["current_rate"]
)

# endregion

# region Serializer definitions for types of auth use

UserInfo = generate_labeler_serializer(
    name="UserInfo",
    klass=dataclasses.UserInfo,
    labels=[
        "id",
        "email",
        "username",
        "mts_account_create",
        "verified",
        "verification_level",
        "_PLACEHOLDER",
        "timezone",
        "locale",
        "company",
        "email_verified",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "mts_master_account_create",
        "group_id",
        "master_account_id",
        "inherit_master_account_verification",
        "is_group_master",
        "group_withdraw_enabled",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "ppt_enabled",
        "merchant_enabled",
        "competition_enabled",
        "two_factors_authentication_modes",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "is_securities_master",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "securities_enabled",
        "allow_disable_ctxswitch",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "time_last_login",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "ctxtswitch_disabled",
        "_PLACEHOLDER",
        "comp_countries",
        "compl_countries_resid",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "is_merchant_enterprise",
    ],
)

LoginHistory = generate_labeler_serializer(
    name="LoginHistory",
    klass=dataclasses.LoginHistory,
    labels=[
        "id",
        "_PLACEHOLDER",
        "time",
        "_PLACEHOLDER",
        "ip",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "extra_info",
    ],
)

BalanceAvailable = generate_labeler_serializer(
    name="BalanceAvailable", klass=dataclasses.BalanceAvailable, labels=["amount"]
)

Order = generate_labeler_serializer(
    name="Order",
    klass=dataclasses.Order,
    labels=[
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
        "meta",
    ],
)

Position = generate_labeler_serializer(
    name="Position",
    klass=dataclasses.Position,
    labels=[
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
        "meta",
    ],
)

Trade = generate_labeler_serializer(
    name="Trade",
    klass=dataclasses.Trade,
    labels=[
        "id",
        "symbol",
        "mts_create",
        "order_id",
        "exec_amount",
        "exec_price",
        "order_type",
        "order_price",
        "maker",
        "fee",
        "fee_currency",
        "cid",
    ],
)

FundingTrade = generate_labeler_serializer(
    name="FundingTrade",
    klass=dataclasses.FundingTrade,
    labels=["id", "currency", "mts_create", "offer_id", "amount", "rate", "period"],
)

OrderTrade = generate_labeler_serializer(
    name="OrderTrade",
    klass=dataclasses.OrderTrade,
    labels=[
        "id",
        "symbol",
        "mts_create",
        "order_id",
        "exec_amount",
        "exec_price",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "maker",
        "fee",
        "fee_currency",
        "cid",
    ],
)

Ledger = generate_labeler_serializer(
    name="Ledger",
    klass=dataclasses.Ledger,
    labels=[
        "id",
        "currency",
        "_PLACEHOLDER",
        "mts",
        "_PLACEHOLDER",
        "amount",
        "balance",
        "_PLACEHOLDER",
        "description",
    ],
)

FundingOffer = generate_labeler_serializer(
    name="FundingOffer",
    klass=dataclasses.FundingOffer,
    labels=[
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
        "_PLACEHOLDER",
    ],
)

FundingCredit = generate_labeler_serializer(
    name="FundingCredit",
    klass=dataclasses.FundingCredit,
    labels=[
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
        "position_pair",
    ],
)

FundingLoan = generate_labeler_serializer(
    name="FundingLoan",
    klass=dataclasses.FundingLoan,
    labels=[
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
    ],
)

FundingAutoRenew = generate_labeler_serializer(
    name="FundingAutoRenew",
    klass=dataclasses.FundingAutoRenew,
    labels=["currency", "period", "rate", "threshold"],
)

FundingInfo = generate_labeler_serializer(
    name="FundingInfo",
    klass=dataclasses.FundingInfo,
    labels=[
        "_PLACEHOLDER",
        "symbol",
        "yield_loan",
        "yield_lend",
        "duration_loan",
        "duration_lend",
    ],
    flat=True,
)

Wallet = generate_labeler_serializer(
    name="Wallet",
    klass=dataclasses.Wallet,
    labels=[
        "wallet_type",
        "currency",
        "balance",
        "unsettled_interest",
        "available_balance",
        "last_change",
        "trade_details",
    ],
)

Transfer = generate_labeler_serializer(
    name="Transfer",
    klass=dataclasses.Transfer,
    labels=[
        "mts",
        "wallet_from",
        "wallet_to",
        "_PLACEHOLDER",
        "currency",
        "currency_to",
        "_PLACEHOLDER",
        "amount",
    ],
)

Withdrawal = generate_labeler_serializer(
    name="Withdrawal",
    klass=dataclasses.Withdrawal,
    labels=[
        "withdrawal_id",
        "_PLACEHOLDER",
        "method",
        "payment_id",
        "wallet",
        "amount",
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "withdrawal_fee",
    ],
)

DepositAddress = generate_labeler_serializer(
    name="DepositAddress",
    klass=dataclasses.DepositAddress,
    labels=[
        "_PLACEHOLDER",
        "method",
        "currency_code",
        "_PLACEHOLDER",
        "address",
        "pool_address",
    ],
)

LightningNetworkInvoice = generate_labeler_serializer(
    name="LightningNetworkInvoice",
    klass=dataclasses.LightningNetworkInvoice,
    labels=["invoice_hash", "invoice", "_PLACEHOLDER", "_PLACEHOLDER", "amount"],
)

Movement = generate_labeler_serializer(
    name="Movement",
    klass=dataclasses.Movement,
    labels=[
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
        "withdraw_transaction_note",
    ],
)

SymbolMarginInfo = generate_labeler_serializer(
    name="SymbolMarginInfo",
    klass=dataclasses.SymbolMarginInfo,
    labels=[
        "_PLACEHOLDER",
        "symbol",
        "tradable_balance",
        "gross_balance",
        "buy",
        "sell",
    ],
    flat=True,
)

BaseMarginInfo = generate_labeler_serializer(
    name="BaseMarginInfo",
    klass=dataclasses.BaseMarginInfo,
    labels=[
        "_PLACEHOLDER",
        "user_pl",
        "user_swaps",
        "margin_balance",
        "margin_net",
        "margin_min",
    ],
    flat=True,
)

PositionClaim = generate_labeler_serializer(
    name="PositionClaim",
    klass=dataclasses.PositionClaim,
    labels=[
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
        "meta",
    ],
)

PositionIncreaseInfo = generate_labeler_serializer(
    name="PositionIncreaseInfo",
    klass=dataclasses.PositionIncreaseInfo,
    labels=[
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
        "_PLACEHOLDER",
        "_PLACEHOLDER",
        "funding_value",
        "funding_required",
        "funding_value_currency",
        "funding_required_currency",
    ],
    flat=True,
)

PositionIncrease = generate_labeler_serializer(
    name="PositionIncrease",
    klass=dataclasses.PositionIncrease,
    labels=["symbol", "_PLACEHOLDER", "amount", "base_price"],
)

PositionHistory = generate_labeler_serializer(
    name="PositionHistory",
    klass=dataclasses.PositionHistory,
    labels=[
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
    ],
)

PositionSnapshot = generate_labeler_serializer(
    name="PositionSnapshot",
    klass=dataclasses.PositionSnapshot,
    labels=[
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
    ],
)

PositionAudit = generate_labeler_serializer(
    name="PositionAudit",
    klass=dataclasses.PositionAudit,
    labels=[
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
        "meta",
    ],
)

DerivativePositionCollateral = generate_labeler_serializer(
    name="DerivativePositionCollateral",
    klass=dataclasses.DerivativePositionCollateral,
    labels=["status"],
)

DerivativePositionCollateralLimits = generate_labeler_serializer(
    name="DerivativePositionCollateralLimits",
    klass=dataclasses.DerivativePositionCollateralLimits,
    labels=["min_collateral", "max_collateral"],
)

BalanceInfo = generate_labeler_serializer(
    name="BalanceInfo",
    klass=dataclasses.BalanceInfo,
    labels=["aum", "aum_net"],
)

# endregion
