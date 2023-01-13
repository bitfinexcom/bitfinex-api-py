from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

from types import SimpleNamespace

from .. notification import Notification

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for Rest Public Endpoints

class PlatformStatus(SimpleNamespace):
    OPERATIVE: int

class TradingPairTicker(SimpleNamespace):
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

class FundingCurrencyTicker(SimpleNamespace):
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

class TickersHistory(SimpleNamespace):
    SYMBOL: str
    BID: float
    ASK: float
    MTS: int

class TradingPairTrade(SimpleNamespace):
    ID: int 
    MTS: int 
    AMOUNT: float 
    PRICE: float

class FundingCurrencyTrade(SimpleNamespace):
    ID: int 
    MTS: int 
    AMOUNT: float 
    RATE: float 
    PERIOD: int

class TradingPairBook(SimpleNamespace):
    PRICE: float 
    COUNT: int 
    AMOUNT: float
    
class FundingCurrencyBook(SimpleNamespace):
    RATE: float 
    PERIOD: int 
    COUNT: int 
    AMOUNT: float
        
class TradingPairRawBook(SimpleNamespace):
    ORDER_ID: int
    PRICE: float 
    AMOUNT: float
            
class FundingCurrencyRawBook(SimpleNamespace):
    OFFER_ID: int 
    PERIOD: int 
    RATE: float 
    AMOUNT: float

class Statistic(SimpleNamespace):
    MTS: int
    VALUE: float

class Candle(SimpleNamespace):
    MTS: int
    OPEN: float
    CLOSE: float
    HIGH: float
    LOW: float
    VOLUME: float

class DerivativesStatus(SimpleNamespace):
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

class Liquidation(SimpleNamespace):
    POS_ID: int
    MTS: int
    SYMBOL: str
    AMOUNT: float
    BASE_PRICE: float
    IS_MATCH: int
    IS_MARKET_SOLD: int
    PRICE_ACQUIRED: float

class Leaderboard(SimpleNamespace):
    MTS: int
    USERNAME: str
    RANKING: int
    VALUE: float
    TWITTER_HANDLE: Optional[str]

class FundingStatistic(SimpleNamespace): 
    TIMESTAMP: int
    FRR: float
    AVG_PERIOD: float
    FUNDING_AMOUNT: float
    FUNDING_AMOUNT_USED: float
    FUNDING_BELOW_THRESHOLD: float

#endregion

#region Type hinting for Rest Authenticated Endpoints

class Wallet(SimpleNamespace):
    WALLET_TYPE: str
    CURRENCY: str
    BALANCE: float
    UNSETTLED_INTEREST: float
    AVAILABLE_BALANCE: float
    LAST_CHANGE: str
    TRADE_DETAILS: JSON

class Order(SimpleNamespace):
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

class Position(SimpleNamespace):
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

class FundingOffer(SimpleNamespace):
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
    
class Trade(SimpleNamespace):
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

class OrderTrade(SimpleNamespace):
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

class Ledger(SimpleNamespace):
    ID: int
    CURRENCY: str 
    MTS: int
    AMOUNT: float
    BALANCE: float
    description: str

class FundingCredit(SimpleNamespace):
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

#endregion