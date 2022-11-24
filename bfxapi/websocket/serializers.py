from .exceptions import BfxWebsocketException

class _Serializer(object):
    def __init__(self, name, labels):
        self.name, self.__labels = name, labels

    def __serialize(self, *args, IGNORE = [ "_PLACEHOLDER" ]):
        if len(self.__labels) != len(args):
            raise BfxWebsocketException("<self.__labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(self.__labels):
            if label not in IGNORE:
                yield label, args[index]

    def parse(self, *values):
        return dict(self.__serialize(*values))

#region Serializers definition for Websocket Public Channels

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

DerivativesStatus = _Serializer("DerivativesStatus", labels=[
    "TIME_MS",
    "_PLACEHOLDER", 
    "DERIV_PRICE",
    "SPOT_PRICE",
    "_PLACEHOLDER",
    "INSURANCE_FUND_BALANCE",
    "_PLACEHOLDER",
    "NEXT_FUNDING_EVT_TIMESTAMP_MS",
    "NEXT_FUNDING_ACCRUED",
    "NEXT_FUNDING_STEP",
    "_PLACEHOLDER",
    "CURRENT_FUNDING"
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "MARK_PRICE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "OPEN_INTEREST",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "CLAMP_MIN",
    "CLAMP_MAX"
])

#endregion

#region Serializers definition for Websocket Authenticated Channels

Order = _Serializer("Order", labels=[
    "ID",
    "GID",
    "CID",
    "SYMBOL",
    "MTS_CREATE", 
    "MTS_UPDATE", 
    "AMOUNT", 
    "AMOUNT_ORIG", 
    "ORDER_TYPE",
    "TYPE_PREV",
    "MTS_TIF",
    "_PLACEHOLDER",
    "FLAGS",
    "ORDER_STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "PRICE",
    "PRICE_AVG",
    "PRICE_TRAILING",
    "PRICE_AUX_LIMIT",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "NOTIFY",
    "HIDDEN", 
    "PLACED_ID",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "ROUTING",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "META"
])

Position = _Serializer("Position", labels=[
    "SYMBOL", 
    "STATUS", 
    "AMOUNT", 
    "BASE_PRICE", 
    "MARGIN_FUNDING", 
    "MARGIN_FUNDING_TYPE",
    "PL",
    "PL_PERC",
    "PRICE_LIQ",
    "LEVERAGE",
    "FLAG",
    "POSITION_ID",
    "MTS_CREATE",
    "MTS_UPDATE",
    "_PLACEHOLDER",
    "TYPE",
    "_PLACEHOLDER",
    "COLLATERAL",
    "COLLATERAL_MIN",
    "META"
])

TradeExecuted = _Serializer("TradeExecuted", labels=[
    "ID", 
    "SYMBOL", 
    "MTS_CREATE",
    "ORDER_ID", 
    "EXEC_AMOUNT", 
    "EXEC_PRICE", 
    "ORDER_TYPE", 
    "ORDER_PRICE", 
    "MAKER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "CID"
])

TradeExecutionUpdate = _Serializer("TradeExecutionUpdate", labels=[
    "ID", 
    "SYMBOL", 
    "MTS_CREATE",
    "ORDER_ID", 
    "EXEC_AMOUNT", 
    "EXEC_PRICE", 
    "ORDER_TYPE", 
    "ORDER_PRICE", 
    "MAKER",
    "FEE",
    "FEE_CURRENCY",
    "CID"
])

FundingOffer = _Serializer("FundingOffer", labels=[
    "ID",
    "SYMBOL",
    "MTS_CREATED",
    "MTS_UPDATED",
    "AMOUNT",
    "AMOUNT_ORIG",
    "OFFER_TYPE",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "_PLACEHOLDER"
])

FundingCredit = _Serializer("FundingCredit", labels=[
    "ID",
    "SYMBOL",
    "SIDE",
    "MTS_CREATE",
    "MTS_UPDATE",
    "AMOUNT",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "MTS_OPENING",
    "MTS_LAST_PAYOUT",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "RATE_REAL",
    "NO_CLOSE",
    "POSITION_PAIR"
])

FundingLoan = _Serializer("FundingLoan", labels=[
    "ID",
    "SYMBOL",
    "SIDE",
    "MTS_CREATE",
    "MTS_UPDATE",
    "AMOUNT",
    "FLAGS",
    "STATUS",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "_PLACEHOLDER",
    "RATE",
    "PERIOD",
    "MTS_OPENING",
    "MTS_LAST_PAYOUT",
    "NOTIFY",
    "HIDDEN",
    "_PLACEHOLDER",
    "RENEW",
    "RATE_REAL",
    "NO_CLOSE"
])

Wallet = _Serializer("Wallet", labels=[
    "WALLET_TYPE", 
    "CURRENCY", 
    "BALANCE", 
    "UNSETTLED_INTEREST",
    "BALANCE_AVAILABLE",
    "DESCRIPTION",
    "META"
])

BalanceInfo = _Serializer("BalanceInfo", labels=[
    "AUM", 
    "AUM_NET", 
])

#endregion

#region Serializers definition for Notifications channel

Notification = _Serializer("Notification", labels=[
    "MTS",
    "TYPE",
    "MESSAGE_ID",
    "_PLACEHOLDER",
    "NOTIFY_INFO",
    "CODE",
    "STATUS",
    "TEXT"
])

#endregion