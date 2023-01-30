from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

from dataclasses import dataclass

from .. labeler import _Type
from .. notification import Notification
from .. utils.encoder import JSON

#region Type hinting for Rest Public Endpoints

@dataclass
class PlatformStatus(_Type):
    status: int

@dataclass
class TradingPairTicker(_Type):
    symbol: Optional[str]
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    daily_change: float
    daily_change_relative: float
    last_price: float
    volume: float
    high: float
    low: float

@dataclass
class FundingCurrencyTicker(_Type):
    symbol: Optional[str]
    frr: float
    bid: float
    bid_period: int
    bid_size: float
    ask: float
    ask_period: int
    ask_size: float
    daily_change: float
    daily_change_relative: float
    last_price: float
    volume: float
    high: float
    low: float
    frr_amount_available: float

@dataclass
class TickersHistory(_Type):
    symbol: str
    bid: float
    ask: float
    mts: int

@dataclass
class TradingPairTrade(_Type):
    id: int 
    mts: int 
    amount: float 
    price: float

@dataclass
class FundingCurrencyTrade(_Type):
    id: int 
    mts: int 
    amount: float 
    rate: float 
    period: int

@dataclass
class TradingPairBook(_Type):
    price: float 
    count: int 
    amount: float
    
@dataclass
class FundingCurrencyBook(_Type):
    rate: float 
    period: int 
    count: int 
    amount: float

@dataclass        
class TradingPairRawBook(_Type):
    order_id: int
    price: float 
    amount: float

@dataclass           
class FundingCurrencyRawBook(_Type):
    offer_id: int 
    period: int 
    rate: float 
    amount: float

@dataclass
class Statistic(_Type):
    mts: int
    value: float

@dataclass
class Candle(_Type):
    mts: int
    open: float
    close: float
    high: float
    low: float
    volume: float

@dataclass
class DerivativesStatus(_Type):
    key: Optional[str]
    mts: int
    deriv_price: float
    spot_price: float
    insurance_fund_balance: float
    next_funding_evt_timestamp_ms: int
    next_funding_accrued: float
    next_funding_step: int
    current_funding: float
    mark_price: float
    open_interest: float
    clamp_min: float
    clamp_max: float

@dataclass
class Liquidation(_Type):
    pos_id: int
    mts: int
    symbol: str
    amount: float
    base_price: float
    is_match: int
    is_market_sold: int
    price_acquired: float

@dataclass
class Leaderboard(_Type):
    mts: int
    username: str
    ranking: int
    value: float
    twitter_handle: Optional[str]

@dataclass
class FundingStatistic(_Type): 
    timestamp: int
    frr: float
    avg_period: float
    funding_amount: float
    funding_amount_used: float
    funding_below_threshold: float

@dataclass
class PulseProfile(_Type):
    puid: str
    mts: int
    nickname: str
    picture: str
    text: str
    twitter_handle: str
    followers: int
    following: int
    tipping_status: int

@dataclass
class PulseMessage(_Type):
    pid: str
    mts: int
    puid: str
    title: str
    content: str
    is_pin: int
    is_public: int
    comments_disabled: int
    tags: List[str]
    attachments: List[str]
    meta: List[JSON]
    likes: int
    profile: PulseProfile
    comments: int

@dataclass
class TradingMarketAveragePrice(_Type):
    price_avg: float
    amount: float

@dataclass
class FundingMarketAveragePrice(_Type):
    rate_avg: float
    amount: float

@dataclass
class FxRate(_Type):
    current_rate: float

#endregion

#region Type hinting for Rest Authenticated Endpoints

@dataclass
class Wallet(_Type):
    wallet_type: str
    currency: str
    balance: float
    unsettled_interest: float
    available_balance: float
    last_change: str
    trade_details: JSON

@dataclass
class Order(_Type):
    id: int
    gid: int
    cid: int
    symbol: str
    mts_create: int
    mts_update: int
    amount: float
    amount_orig: float
    order_type: str
    type_prev: str
    mts_tif: int
    flags: int
    order_status: str
    price: float
    price_avg: float
    price_trailing: float
    price_aux_limit: float
    notify: int
    hidden: int
    placed_id: int
    routing: str
    meta: JSON

@dataclass
class Position(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    margin_funding: float
    margin_funding_type: int
    pl: float
    pl_perc: float
    price_liq: float
    leverage: float
    position_id: int
    mts_create: int
    mts_update: int
    type: int
    collateral: float
    collateral_min: float
    meta: JSON

@dataclass
class FundingOffer(_Type):
    id: int
    symbol: str
    mts_create: int
    mts_update: int
    amount: float
    amount_orig: float
    offer_type: str
    flags: int
    offer_status: str
    rate: float
    period: int
    notify: bool
    hidden: int
    renew: bool

@dataclass
class Trade(_Type):
    id: int 
    symbol: str 
    mts_create: int
    order_id: int 
    exec_amount: float 
    exec_price: float 
    order_type: str 
    order_price: float 
    maker:int
    fee: float
    fee_currency: str
    cid: int

@dataclass
class OrderTrade(_Type):
    id: int 
    symbol: str 
    mts_create: int
    order_id: int 
    exec_amount: float 
    exec_price: float 
    maker:int
    fee: float
    fee_currency: str
    cid: int

@dataclass
class Ledger(_Type):
    id: int
    currency: str 
    mts: int
    amount: float
    balance: float
    description: str

@dataclass
class FundingLoan(_Type):
    id: int
    symbol: str
    side: int
    mts_create: int
    mts_update: int
    amount: float
    flags: int
    status: str
    rate: float
    period: int
    mts_opening: int
    mts_last_payout: int
    notify: int
    hidden: int
    renew: int
    rate_real: float
    no_close: int

@dataclass
class FundingCredit(_Type):
    id: int
    symbol: str
    side: int
    mts_create: int
    mts_update: int
    amount: float
    flags: int
    status: str
    rate: float
    period: int
    mts_opening: int
    mts_last_payout: int
    notify: int
    hidden: int
    renew: int
    rate_real: float
    no_close: int
    position_pair: str

@dataclass
class Transfer(_Type):
    mts: int
    wallet_from: str
    wallet_to: str
    currency: str
    currency_to: str
    amount: int

@dataclass
class Withdrawal(_Type):
    withdrawal_id: int
    method: str
    payment_id: str
    wallet: str
    amount: float
    withdrawal_fee: float

@dataclass
class DepositAddress(_Type):
    method: str
    currency_code: str
    address: str
    pool_address: str

@dataclass
class Invoice(_Type):
    invoice_hash: str
    invoice: str
    amount: str

@dataclass
class Movement(_Type):
    id: str
    currency: str
    currency_name: str
    mts_start: int
    mts_update: int
    status: str
    amount: int
    fees: int
    destination_address: str
    transaction_id: str
    withdraw_transaction_note: str
    
@dataclass
class SymbolMarginInfo(_Type):
    symbol: str
    tradable_balance: float
    gross_balance: float
    buy: float
    sell: float

@dataclass
class BaseMarginInfo(_Type):
    user_pl: float
    user_swaps: float
    margin_balance: float
    margin_net: float
    margin_min: float

@dataclass
class Claim(_Type):
    symbol: str
    position_status: str
    amount: float
    base_price: float
    margin_funding: float
    margin_funding_type: int
    position_id: int
    mts_create: int
    mts_update: int
    pos_type: int
    collateral: str
    min_collateral: str
    meta: JSON

@dataclass
class IncreaseInfo(_Type):
    max_pos: int
    current_pos: float
    base_currency_balance: float
    tradable_balance_quote_currency: float
    tradable_balance_quote_total: float
    tradable_balance_base_currency: float
    tradable_balance_base_total: float
    funding_avail: float
    funding_value: float
    funding_required: float
    funding_value_currency: str
    funding_required_currency: str

@dataclass
class Increase(_Type):
    symbol: str
    amount: float
    base_price: float

@dataclass
class PositionHistory(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int

@dataclass
class PositionSnapshot(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int

@dataclass
class PositionAudit(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int
    type: int
    collateral: float
    collateral_min: float
    meta: JSON

@dataclass
class DerivativePositionCollateral(_Type):
    status: int

@dataclass
class DerivativePositionCollateralLimits(_Type):
    min_collateral: float
    max_collateral: float

#endregion