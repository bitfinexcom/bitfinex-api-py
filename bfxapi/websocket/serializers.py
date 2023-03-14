#pylint: disable=duplicate-code

from . import types

from .. labeler import generate_labeler_serializer

#pylint: disable-next=unused-import
from .. notification import _Notification

__serializers__ = [
    "TradingPairTicker", "FundingCurrencyTicker", "TradingPairTrade",
    "FundingCurrencyTrade", "TradingPairBook", "FundingCurrencyBook",
    "TradingPairRawBook", "FundingCurrencyRawBook", "Candle",
    "DerivativesStatus",

    "Order", "Position", "Trade",
    "FundingOffer", "FundingCredit", "FundingLoan",
    "Wallet", "Balance",
]

#region Serializers definition for Websocket Public Channels

TradingPairTicker = generate_labeler_serializer(
    name="TradingPairTicker",
    klass=types.TradingPairTicker,
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
        "low"
    ]
)

FundingCurrencyTicker = generate_labeler_serializer(
    name="FundingCurrencyTicker",
    klass=types.FundingCurrencyTicker,
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
        "frr_amount_available"
    ]
)

TradingPairTrade = generate_labeler_serializer(
    name="TradingPairTrade",
    klass=types.TradingPairTrade,
    labels=[
        "id", 
        "mts", 
        "amount", 
        "price"
    ]
)

FundingCurrencyTrade = generate_labeler_serializer(
    name="FundingCurrencyTrade",
    klass=types.FundingCurrencyTrade,
    labels=[
        "id", 
        "mts", 
        "amount", 
        "rate", 
        "period"
    ]
)

TradingPairBook = generate_labeler_serializer(
    name="TradingPairBook",
    klass=types.TradingPairBook,
    labels=[
        "price", 
        "count", 
        "amount"
    ]
)

FundingCurrencyBook = generate_labeler_serializer(
    name="FundingCurrencyBook",
    klass=types.FundingCurrencyBook,
    labels=[
        "rate",
        "period",
        "count",
        "amount"
    ]
)

TradingPairRawBook = generate_labeler_serializer(
    name="TradingPairRawBook",
    klass=types.TradingPairRawBook,
    labels=[
        "order_id",
        "price",
        "amount"
    ]
)

FundingCurrencyRawBook = generate_labeler_serializer(
    name="FundingCurrencyRawBook",
    klass=types.FundingCurrencyRawBook,
    labels=[
        "offer_id", 
        "period", 
        "rate", 
        "amount"
    ]
)

Candle = generate_labeler_serializer(
    name="Candle",
    klass=types.Candle,
    labels=[
        "mts", 
        "open", 
        "close", 
        "high", 
        "low", 
        "volume"
    ]
)

DerivativesStatus = generate_labeler_serializer(
    name="DerivativesStatus",
    klass=types.DerivativesStatus,
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
        "clamp_max"
    ]
)

#endregion

#region Serializers definition for Websocket Authenticated Channels

Order = generate_labeler_serializer(
    name="Order",
    klass=types.Order,
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
        "meta"
    ]
)

Position = generate_labeler_serializer(
    name="Position",
    klass=types.Position,
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
        "flag",
        "position_id",
        "mts_create",
        "mts_update",
        "_PLACEHOLDER",
        "type",
        "_PLACEHOLDER",
        "collateral",
        "collateral_min",
        "meta"
    ]
)

Trade = generate_labeler_serializer(
    name="Trade",
    klass=types.Trade,
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
        "cid"
    ]
)

FundingOffer = generate_labeler_serializer(
    name="FundingOffer",
    klass=types.FundingOffer,
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
        "_PLACEHOLDER"
    ]
)

FundingCredit = generate_labeler_serializer(
    name="FundingCredit",
    klass=types.FundingCredit,
    labels=[
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
        "_PLACEHOLDER",
        "no_close",
        "position_pair"
    ]
)

FundingLoan = generate_labeler_serializer(
    name="FundingLoan",
    klass=types.FundingLoan,
    labels=[
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
        "_PLACEHOLDER",
        "no_close"
    ]
)

Wallet = generate_labeler_serializer(
    name="Wallet",
    klass=types.Wallet,
    labels=[
        "wallet_type", 
        "currency", 
        "balance", 
        "unsettled_interest",
        "available_balance",
        "last_change",
        "trade_details"
    ]
)

Balance = generate_labeler_serializer(
    name="Balance",
    klass=types.Balance,
    labels=[
        "aum", 
        "aum_net"
    ]
)

#endregion
