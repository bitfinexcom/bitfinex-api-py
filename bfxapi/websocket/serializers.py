from .errors import BfxWebsocketException

class _Serializer(object):
    def __init__(self, name, labels):
        self.name, self.__labels = name, labels

    def __serialize(self, *args, IGNORE = [ "_PLACEHOLDER" ]):
        if len(self.__labels) != len(args):
            raise BfxWebsocketException("<self.__labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(self.__labels):
            if label not in IGNORE:
                yield label, args[index]

    def __call__(self, *values):
        return dict(self.__serialize(*values))

TradingPairTicker = _Serializer("TradingPairTicker", labels=[
    "BID",
    "BID_SIZE",
    "ASK",
    "ASK_SIZE",
    "DAILY_CHANGE",
    "DAILY_CHANGE_RELATIVE",
    "LAST_PRICE",
    "VOLUME",
    "HIGH",
    "LOW"
])

FundingCurrencyTicker = _Serializer("FundingCurrencyTicker", labels=[
    "FRR",
    "BID",
    "BID_PERIOD",
    "BID_SIZE",
    "ASK",
    "ASK_PERIOD",
    "ASK_SIZE",
    "DAILY_CHANGE",
    "DAILY_CHANGE_RELATIVE",
    "LAST_PRICE",
    "VOLUME",
    "HIGH",
    "LOW"
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FRR_AMOUNT_AVAILABLE"
])

TradingPairTrade = _Serializer("TradingPairTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "PRICE" 
])

FundingCurrencyTrade = _Serializer("FundingCurrencyTrade", labels=[ 
    "ID", 
    "MTS", 
    "AMOUNT", 
    "RATE", 
    "PERIOD" 
])

TradingPairBook = _Serializer("TradingPairBook", labels=[
    "PRICE", 
    "COUNT", 
    "AMOUNT"
])

FundingCurrencyBook = _Serializer("FundingCurrencyBook", labels=[
    "RATE", 
    "PERIOD", 
    "COUNT", 
    "AMOUNT"
])

TradingPairRawBook = _Serializer("TradingPairRawBook", labels=[
    "ORDER_ID", 
    "PRICE", 
    "AMOUNT"
])

FundingCurrencyRawBook = _Serializer("FundingCurrencyRawBook", labels=[
    "OFFER_ID", 
    "PERIOD", 
    "RATE", 
    "AMOUNT"
])

Candle = _Serializer("Candle", labels=[
    "MTS", 
    "OPEN", 
    "CLOSE", 
    "HIGH", 
    "LOW", 
    "VOLUME"
])