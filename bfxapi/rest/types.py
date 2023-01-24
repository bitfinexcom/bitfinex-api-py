from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

from dataclasses import dataclass

from .. labeler import _Type

from .. notification import Notification

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for Rest Public Endpoints

@dataclass
class PlatformStatus(_Type):
    STATUS: int

@dataclass
class TradingPairTicker(_Type):
    SYMBOL: Optional[str]
    BID: float
    BID_SIZE: float
    ASK: float
    ASK_SIZE: float
    DAILY_CHANGE: float
    DAILY_CHANGE_RELATIVE: float
    LAST_PRICE: float
    VOLUME: float
    HIGH: float
    LOW: float

@dataclass
class FundingCurrencyTicker(_Type):
    SYMBOL: Optional[str]
    FRR: float
    BID: float
    BID_PERIOD: int
    BID_SIZE: float
    ASK: float
    ASK_PERIOD: int
    ASK_SIZE: float
    DAILY_CHANGE: float
    DAILY_CHANGE_RELATIVE: float
    LAST_PRICE: float
    VOLUME: float
    HIGH: float
    LOW: float
    FRR_AMOUNT_AVAILABLE: float

@dataclass
class TickersHistory(_Type):
    SYMBOL: str
    BID: float
    ASK: float
    MTS: int

@dataclass
class TradingPairTrade(_Type):
    ID: int 
    MTS: int 
    AMOUNT: float 
    PRICE: float

@dataclass
class FundingCurrencyTrade(_Type):
    ID: int 
    MTS: int 
    AMOUNT: float 
    RATE: float 
    PERIOD: int

@dataclass
class TradingPairBook(_Type):
    PRICE: float 
    COUNT: int 
    AMOUNT: float
    
@dataclass
class FundingCurrencyBook(_Type):
    RATE: float 
    PERIOD: int 
    COUNT: int 
    AMOUNT: float

@dataclass        
class TradingPairRawBook(_Type):
    ORDER_ID: int
    PRICE: float 
    AMOUNT: float

@dataclass           
class FundingCurrencyRawBook(_Type):
    OFFER_ID: int 
    PERIOD: int 
    RATE: float 
    AMOUNT: float

@dataclass
class Statistic(_Type):
    MTS: int
    VALUE: float

@dataclass
class Candle(_Type):
    MTS: int
    OPEN: float
    CLOSE: float
    HIGH: float
    LOW: float
    VOLUME: float

@dataclass
class DerivativesStatus(_Type):
    KEY: Optional[str]
    MTS: int
    DERIV_PRICE: float
    SPOT_PRICE: float
    INSURANCE_FUND_BALANCE: float
    NEXT_FUNDING_EVT_TIMESTAMP_MS: int
    NEXT_FUNDING_ACCRUED: float
    NEXT_FUNDING_STEP: int
    CURRENT_FUNDING: float
    MARK_PRICE: float
    OPEN_INTEREST: float
    CLAMP_MIN: float
    CLAMP_MAX: float

@dataclass
class Liquidation(_Type):
    POS_ID: int
    MTS: int
    SYMBOL: str
    AMOUNT: float
    BASE_PRICE: float
    IS_MATCH: int
    IS_MARKET_SOLD: int
    PRICE_ACQUIRED: float

@dataclass
class Leaderboard(_Type):
    MTS: int
    USERNAME: str
    RANKING: int
    VALUE: float
    TWITTER_HANDLE: Optional[str]

@dataclass
class FundingStatistic(_Type): 
    TIMESTAMP: int
    FRR: float
    AVG_PERIOD: float
    FUNDING_AMOUNT: float
    FUNDING_AMOUNT_USED: float
    FUNDING_BELOW_THRESHOLD: float

@dataclass
class PulseProfile(_Type):
    PUID: str
    MTS: int
    NICKNAME: str
    PICTURE: str
    TEXT: str
    TWITTER_HANDLE: str
    FOLLOWERS: int
    FOLLOWING: int
    TIPPING_STATUS: int

@dataclass
class PulseMessage(_Type):
    PID: str
    MTS: int
    PUID: str
    TITLE: str
    CONTENT: str
    IS_PIN: int
    IS_PUBLIC: int
    COMMENTS_DISABLED: int
    TAGS: List[str]
    ATTACHMENTS: List[str]
    META: List[JSON]
    LIKES: int
    PROFILE: PulseProfile
    COMMENTS: int

@dataclass
class TradingMarketAveragePrice(_Type):
    PRICE_AVG: float
    AMOUNT: float

@dataclass
class FundingMarketAveragePrice(_Type):
    RATE_AVG: float
    AMOUNT: float

#endregion

#region Type hinting for Rest Authenticated Endpoints

@dataclass
class Wallet(_Type):
    WALLET_TYPE: str
    CURRENCY: str
    BALANCE: float
    UNSETTLED_INTEREST: float
    AVAILABLE_BALANCE: float
    LAST_CHANGE: str
    TRADE_DETAILS: JSON

@dataclass
class Order(_Type):
    ID: int
    GID: int
    CID: int
    SYMBOL: str
    MTS_CREATE: int
    MTS_UPDATE: int
    AMOUNT: float
    AMOUNT_ORIG: float
    ORDER_TYPE: str
    TYPE_PREV: str
    MTS_TIF: int
    FLAGS: int
    ORDER_STATUS: str
    PRICE: float
    PRICE_AVG: float
    PRICE_TRAILING: float
    PRICE_AUX_LIMIT: float
    NOTIFY: int
    HIDDEN: int
    PLACED_ID: int
    ROUTING: str
    META: JSON

@dataclass
class Position(_Type):
    SYMBOL: str
    STATUS: str
    AMOUNT: float
    BASE_PRICE: float
    MARGIN_FUNDING: float
    MARGIN_FUNDING_TYPE: int
    PL: float
    PL_PERC: float
    PRICE_LIQ: float
    LEVERAGE: float
    POSITION_ID: int
    MTS_CREATE: int
    MTS_UPDATE: int
    TYPE: int
    COLLATERAL: float
    COLLATERAL_MIN: float
    META: JSON

@dataclass
class FundingOffer(_Type):
    ID: int
    SYMBOL: str
    MTS_CREATE: int
    MTS_UPDATE: int
    AMOUNT: float
    AMOUNT_ORIG: float
    OFFER_TYPE: str
    FLAGS: int
    OFFER_STATUS: str
    RATE: float
    PERIOD: int
    NOTIFY: bool
    HIDDEN: int
    RENEW: bool
    
@dataclass
class Trade(_Type):
    ID: int 
    SYMBOL: str 
    MTS_CREATE: int
    ORDER_ID: int 
    EXEC_AMOUNT: float 
    EXEC_PRICE: float 
    ORDER_TYPE: str 
    ORDER_PRICE: float 
    MAKER:int
    FEE: float
    FEE_CURRENCY: str
    CID: int

@dataclass
class OrderTrade(_Type):
    ID: int 
    SYMBOL: str 
    MTS_CREATE: int
    ORDER_ID: int 
    EXEC_AMOUNT: float 
    EXEC_PRICE: float 
    MAKER:int
    FEE: float
    FEE_CURRENCY: str
    CID: int

@dataclass
class Ledger(_Type):
    ID: int
    CURRENCY: str 
    MTS: int
    AMOUNT: float
    BALANCE: float
    description: str

@dataclass
class FundingCredit(_Type):
    ID: int
    SYMBOL: str
    SIDE: int
    MTS_CREATE: int
    MTS_UPDATE: int
    AMOUNT: float
    FLAGS: int
    STATUS: str
    RATE: float
    PERIOD: int
    MTS_OPENING: int
    MTS_LAST_PAYOUT: int
    NOTIFY: int
    HIDDEN: int
    RENEW: int
    RATE_REAL: float
    NO_CLOSE: int
    POSITION_PAIR: str

@dataclass
class Transfer(_Type):
    MTS: int
    WALLET_FROM: str
    WALLET_TO: str
    CURRENCY: str
    CURRENCY_TO: str
    AMOUNT: int

@dataclass
class Withdrawal(_Type):
    WITHDRAWAL_ID: int
    METHOD: str
    PAYMENT_ID: str
    WALLET: str
    AMOUNT: float
    WITHDRAWAL_FEE: float

@dataclass
class DepositAddress(_Type):
    METHOD: str
    CURRENCY_CODE: str
    ADDRESS: str
    POOL_ADDRESS: str

@dataclass
class Invoice(_Type):
    INVOICE_HASH: str
    INVOICE: str
    AMOUNT: str

@dataclass
class Movement(_Type):
    ID: str
    CURRENCY: str
    CURRENCY_NAME: str
    MTS_STARTED: int
    MTS_UPDATED: int
    STATUS: str
    AMOUNT: int
    FEES: int
    DESTINATION_ADDRESS: str
    TRANSACTION_ID: str
    WITHDRAW_TRANSACTION_NOTE: str

#endregion