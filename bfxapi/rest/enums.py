#pylint: disable-next=wildcard-import,unused-wildcard-import
from ..enums import *

class Config(str, Enum):
    MAP_CURRENCY_SYM = "pub:map:currency:sym"
    MAP_CURRENCY_LABEL = "pub:map:currency:label"
    MAP_CURRENCY_UNIT = "pub:map:currency:unit"
    MAP_CURRENCY_UNDL = "pub:map:currency:undl"
    MAP_CURRENCY_POOL = "pub:map:currency:pool"
    MAP_CURRENCY_EXPLORER = "pub:map:currency:explorer"
    MAP_CURRENCY_TX_FEE = "pub:map:currency:tx:fee"
    MAP_TX_METHOD = "pub:map:tx:method"

    LIST_PAIR_EXCHANGE = "pub:list:pair:exchange"
    LIST_PAIR_MARGIN = "pub:list:pair:margin"
    LIST_PAIR_FUTURES = "pub:list:pair:futures"
    LIST_PAIR_SECURITIES = "pub:list:pair:securities"
    LIST_CURRENCY = "pub:list:currency"
    LIST_COMPETITIONS = "pub:list:competitions"

    INFO_PAIR = "pub:info:pair"
    INFO_PAIR_FUTURES = "pub:info:pair:futures"
    INFO_TX_STATUS = "pub:info:tx:status"

    SPEC_MARGIN = "pub:spec:margin"
    FEES = "pub:fees"

class Precision(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class Sort(int, Enum):
    ASCENDING = +1
    DESCENDING = -1

class MerchantSettingsKey(str, Enum):
    PREFERRED_FIAT = "bfx_pay_preferred_fiat"
    RECOMMEND_STORE = "bfx_pay_recommend_store"
    NOTIFY_PAYMENT_COMPLETED = "bfx_pay_notify_payment_completed"
    NOTIFY_PAYMENT_COMPLETED_EMAIL = "bfx_pay_notify_payment_completed_email"
    NOTIFY_AUTOCONVERT_EXECUTED = "bfx_pay_notify_autoconvert_executed"
    DUST_BALANCE_UI = "bfx_pay_dust_balance_ui"
    MERCHANT_CUSTOMER_SUPPORT_URL = "bfx_pay_merchant_customer_support_url"
    MERCHANT_UNDERPAID_THRESHOLD = "bfx_pay_merchant_underpaid_threshold"
