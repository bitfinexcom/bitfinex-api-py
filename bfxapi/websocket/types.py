#pylint: disable=duplicate-code

#pylint: disable-next=wildcard-import,unused-wildcard-import
from typing import *

from dataclasses import dataclass

from .. labeler import _Type

#pylint: disable-next=unused-import
from .. notification import Notification

from ..utils.json_encoder import JSON

#region Type hinting for Websocket Public Channels

@dataclass
class TradingPairTicker(_Type):
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
class Candle(_Type):
    mts: int
    open: int
    close: int
    high: int
    low: int
    volume: float

@dataclass
class DerivativesStatus(_Type):
    mts: int
    deriv_price: float
    spot_price: float
    insurance_fund_balance: float
    next_funding_evt_mts: int
    next_funding_accrued: float
    next_funding_step: int
    current_funding: float
    mark_price: float
    open_interest: float
    clamp_min: float
    clamp_max: float

#endregion

#region Type hinting for Websocket Authenticated Channels
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
    flag: int
    position_id: int
    mts_create: int
    mts_update: int
    type: int
    collateral: float
    collateral_min: float
    meta: JSON

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
    fee: Optional[float]
    fee_currency: Optional[str]
    cid: int

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
    notify: int
    hidden: int
    renew: int

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
    no_close: int
    position_pair: str

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
    no_close: int

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
class Balance(_Type):
    aum: float
    aum_net: float

#endregion
