from ..enums import *

class Channels(str, Enum):
    TICKER = "ticker"
    TRADES = "trades"
    BOOK = "book"
    CANDLES = "candles"
    STATUS = "status"