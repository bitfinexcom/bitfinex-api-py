from enum import Enum

class Configs(str, Enum):
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

    SPEC_MARGIN = "pub:spec:margin",
    FEES = "pub:fees"