#pylint: disable-next=wildcard-import,unused-wildcard-import
from ..enums import *

class Channel(str, Enum):
    TICKER = "ticker"
    TRADES = "trades"
    BOOK = "book"
    CANDLES = "candles"
    STATUS = "status"
