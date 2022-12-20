from decimal import Decimal

from datetime import datetime

from typing import Type, Tuple, List, Dict, TypedDict, Union, Optional, Any

from ..utils.integers import Int16, Int32, Int45, Int64

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

#region Type hinting for subscription objects

class Subscriptions:
    class TradingPairTicker(TypedDict):
        chanId: int
        symbol: str
        pair: str

    class FundingCurrencyTicker(TypedDict):
        chanId: int
        symbol: str
        currency: str

    class TradingPairTrades(TypedDict):
        chanId: int
        symbol: str
        pair: str

    class FundingCurrencyTrades(TypedDict):
        chanId: int
        symbol: str
        currency: str

    class Book(TypedDict):
        chanId: int
        symbol: str
        prec: str
        freq: str
        len: str
        subId: int
        pair: str

    class Candles(TypedDict):
        chanId: int
        key: str

    class DerivativesStatus(TypedDict):
        chanId: int
        key: str

#endregion

#region Type hinting for Websocket Public Channels

class TradingPairTicker(TypedDict):
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

class Candle(TypedDict):
    MTS: int
    OPEN: float
    CLOSE: float
    HIGH: float
    LOW: float
    VOLUME: float

class DerivativesStatus(TypedDict):
    TIME_MS: int
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

#endregion

#region Type hinting for Websocket Authenticated Channels

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

class Position(TypedDict):
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

class TradeExecuted(TypedDict):
    ID: int 
    SYMBOL: str 
    MTS_CREATE: int
    ORDER_ID: int 
    EXEC_AMOUNT: float 
    EXEC_PRICE: float 
    ORDER_TYPE: str 
    ORDER_PRICE: float 
    MAKER:int
    CID: int

class TradeExecutionUpdate(TypedDict):
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

class FundingOffer(TypedDict):
    ID: int
    SYMBOL: str
    MTS_CREATED: int
    MTS_UPDATED: int
    AMOUNT: float
    AMOUNT_ORIG: float
    OFFER_TYPE: str
    FLAGS: int
    STATUS: str
    RATE: float
    PERIOD: int
    NOTIFY: int
    HIDDEN: int
    RENEW: int

class FundingCredit(TypedDict):
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

class FundingLoan(TypedDict):
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

class Wallet(TypedDict):
    WALLET_TYPE: str
    CURRENCY: str
    BALANCE: float
    UNSETTLED_INTEREST: float
    BALANCE_AVAILABLE: float
    DESCRIPTION: str
    META: JSON

class BalanceInfo(TypedDict):
    AUM: float
    AUM_NET: float

#endregion

#region Type hinting for Notifications channel

class Notification(TypedDict):
    MTS: int
    TYPE: str 
    MESSAGE_ID: int
    NOTIFY_INFO: JSON
    CODE: int
    STATUS: str
    TEXT: str

#endregion

#region Type hinting for Websocket Authenticated Inputs

class Inputs:
    class Order:
        class New(TypedDict, total=False):
            gid: Union[Int32, int]
            cid: Union[Int45, int]
            type: str
            symbol: str
            amount: Union[Decimal, str]
            price: Union[Decimal, str]
            lev: Union[Int32, int]
            price_trailing: Union[Decimal, str]
            price_aux_limit: Union[Decimal, str]
            price_oco_stop: Union[Decimal, str]
            flags: Union[Int16, int]
            tif: Union[datetime, str]
            meta: JSON

        class Update(TypedDict, total=False):
            id: Union[Int64, int]
            cid: Union[Int45, int]
            cid_date: str
            gid: Union[Int32, int]
            price: Union[Decimal, str]
            amount: Union[Decimal, str]
            lev: Union[Int32, int]
            delta: Union[Decimal, str]
            price_aux_limit: Union[Decimal, str]
            price_trailing: Union[Decimal, str]
            flags: Union[Int16, int]
            tif: Union[datetime, str]

        class Cancel(TypedDict, total=False):
            id: Union[Int64, int]
            cid: Union[Int45, int]
            cid_date: Union[datetime, str]

    class Offer:
        class New(TypedDict, total=False):
            type: str
            symbol: str
            amount: Union[Decimal, str]
            rate: Union[Decimal, str]
            period: Union[Int32, int]
            flags: Union[Int16, int]

        class Cancel(TypedDict, total=False):
            id: Union[Int32, int]
        
#endregion