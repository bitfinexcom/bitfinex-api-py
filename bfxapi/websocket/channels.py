from enum import Enum

class Channels(str, Enum):
    TICKER = "ticker"
    TRADES = "trades"
    BOOK = "book"