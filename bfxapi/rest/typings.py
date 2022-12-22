from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

from .. notification import Notification

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for Rest Public Endpoints

class PlatformStatus(TypedDict):
    OPERATIVE: int

class TradingPairTicker(TypedDict):
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

class FundingCurrencyTicker(TypedDict):
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

class TickersHistory(TypedDict):
    SYMBOL: str
    BID: float
    ASK: float
    MTS: int

class TradingPairTrade(TypedDict):
    ID: int 
    MTS: int 
    AMOUNT: float 
    PRICE: float

class FundingCurrencyTrade(TypedDict):
    ID: int 
    MTS: int 
    AMOUNT: float 
    RATE: float 
    PERIOD: int

class TradingPairBook(TypedDict):
    PRICE: float 
    COUNT: int 
    AMOUNT: float
    
class FundingCurrencyBook(TypedDict):
    RATE: float 
    PERIOD: int 
    COUNT: int 
    AMOUNT: float
        
class TradingPairRawBook(TypedDict):
    ORDER_ID: int
    PRICE: float 
    AMOUNT: float
            
class FundingCurrencyRawBook(TypedDict):
    OFFER_ID: int 
    PERIOD: int 
    RATE: float 
    AMOUNT: float

class Statistic(TypedDict):
    MTS: int
    VALUE: float

class Candle(TypedDict):
    MTS: int
    OPEN: float
    CLOSE: float
    HIGH: float
    LOW: float
    VOLUME: float

class DerivativesStatus(TypedDict):
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

class Liquidation(TypedDict):
    POS_ID: int
    MTS: int
    SYMBOL: str
    AMOUNT: float
    BASE_PRICE: float
    IS_MATCH: int
    IS_MARKET_SOLD: int
    PRICE_ACQUIRED: float

class Leaderboard(TypedDict):
    MTS: int
    USERNAME: str
    RANKING: int
    VALUE: float
    TWITTER_HANDLE: Optional[str]

class FundingStatistic(TypedDict): 
    TIMESTAMP: int
    FRR: float
    AVG_PERIOD: float
    FUNDING_AMOUNT: float
    FUNDING_AMOUNT_USED: float
    FUNDING_BELOW_THRESHOLD: float

#endregion

#region Type hinting for Rest Authenticated Endpoints

class Wallet(TypedDict):
    WALLET_TYPE: str
    CURRENCY: str
    BALANCE: float
    UNSETTLED_INTEREST: float
    AVAILABLE_BALANCE: float
    LAST_CHANGE: str
    TRADE_DETAILS: JSON

class Order(TypedDict):
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

#endregion