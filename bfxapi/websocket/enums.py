from enum import Enum

class Channels(str, Enum):
    TICKER = "ticker"
    TRADES = "trades"
    BOOK = "book"
    CANDLES = "candles"
    STATUS = "status"

class Flags(int, Enum):
    HIDDEN = 64
    CLOSE = 512
    REDUCE_ONLY = 1024
    POST_ONLY = 4096
    OCO = 16384
    NO_VAR_RATES = 524288

class Errors(int, Enum):
    ERR_UNK = 10000
    ERR_GENERIC = 10001
    ERR_CONCURRENCY = 10008
    ERR_PARAMS = 10020
    ERR_CONF_FAIL = 10050
    ERR_AUTH_FAIL = 10100
    ERR_AUTH_PAYLOAD = 10111
    ERR_AUTH_SIG = 10112
    ERR_AUTH_HMAC = 10113
    ERR_AUTH_NONCE = 10114
    ERR_UNAUTH_FAIL = 10200
    ERR_SUB_FAIL = 10300
    ERR_SUB_MULTI = 10301
    ERR_UNSUB_FAIL = 10400
    ERR_READY = 11000