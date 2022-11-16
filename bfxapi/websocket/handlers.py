from enum import Enum

from . import serializers

from .errors import BfxWebsocketException

def _get_sub_dictionary(dictionary, keys):
    return { key: dictionary[key] for key in dictionary if key in keys }

def _label_stream_data(labels, *args, IGNORE = [ "_PLACEHOLDER" ]):
    if len(labels) != len(args):
        raise BfxWebsocketException("<labels> and <*args> arguments should contain the same amount of elements.")

    return { label: args[index] for index, label in enumerate(labels) if label not in IGNORE }

class Channels(str, Enum):
    TICKER = "ticker"
    TRADES = "trades"
    BOOK = "book"
    CANDLES = "candles"
    STATUS = "status"

class PublicChannelsHandler(object):
    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

        self.__handlers = {
            Channels.TICKER: self.__ticker_channel_handler,
            Channels.TRADES: self.__trades_channel_handler,
            Channels.BOOK: self.__book_channel_handler,
            Channels.CANDLES: self.__candles_channel_handler,
        }

    def handle(self, subscription, *stream):
        if channel := subscription["channel"] or channel in self.__handlers.keys():
            return self.__handlers[channel](subscription, *stream)

    def __ticker_channel_handler(self, subscription, *stream):
        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "tp_ticker_update",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                serializers.TradingPairTicker(*stream[0])
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "fc_ticker_update",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                serializers.FundingCurrencyTicker(*stream[0])
            )

    def __trades_channel_handler(self, subscription, *stream):
        if type := stream[0] or type in [ "te", "tu", "fte", "ftu" ]:
            if subscription["symbol"].startswith("t"):
                return self.event_emitter.emit(
                    { "te": "tp_trade_executed", "tu": "tp_trade_execution_update" }[type],
                    _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                    serializers.TradingPairTrade(*stream[1])
                )

            if subscription["symbol"].startswith("f"):
                return self.event_emitter.emit(
                    { "fte": "fc_trade_executed", "ftu": "fc_trade_execution_update" }[type],
                    _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                    serializers.FundingCurrencyTrade(*stream[1])
                )

        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "tp_trades_snapshot",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                [ serializers.TradingPairTrade(*substream) for substream in stream[0] ]
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "fc_trades_snapshot",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                [ serializers.FundingCurrencyTrade(*substream)  for substream in stream[0] ]
            )

    def __book_channel_handler(self, subscription, *stream):
        subscription = _get_sub_dictionary(subscription, [ "chanId", "symbol", "prec", "freq", "len", "subId", "pair" ])

        if subscription["prec"] == "R0":
            _trading_pair_serializer, _funding_currency_serializer, IS_RAW_BOOK = serializers.TradingPairRawBook, serializers.FundingCurrencyRawBook, True
        else: _trading_pair_serializer, _funding_currency_serializer, IS_RAW_BOOK = serializers.TradingPairBook, serializers.FundingCurrencyBook, False

        if all(isinstance(substream, list) for substream in stream[0]):
            return self.event_emitter.emit(
                IS_RAW_BOOK and "raw_book_snapshot" or "book_snapshot",
                subscription, 
                [ { "t": _trading_pair_serializer, "f": _funding_currency_serializer }[subscription["symbol"][0]](*substream) for substream in stream[0] ]
            )

        return self.event_emitter.emit(
            IS_RAW_BOOK and "raw_book_update" or "book_update",
            subscription, 
            { "t": _trading_pair_serializer, "f": _funding_currency_serializer }[subscription["symbol"][0]](*stream[0])
        )
        
    def __candles_channel_handler(self, subscription, *stream):
        subscription = _get_sub_dictionary(subscription, [ "chanId", "key" ])

        if all(isinstance(substream, list) for substream in stream[0]):
            return self.event_emitter.emit(
                "candles_snapshot", 
                subscription, 
                [ serializers.Candle(*substream) for substream in stream[0] ]
            )

        return self.event_emitter.emit(
            "candles_update", 
            subscription, 
            serializers.Candle(*stream[0])
        )

class AuthenticatedChannelsHandler(object):
    def __init__(self, event_emitter, strict = False):
        self.event_emitter, self.strict = event_emitter, strict

        self.__handlers = {
            ("os", "on", "ou", "oc",): self.__orders_channel_handler,
            ("ps", "pn", "pu", "pc",): self.__positions_channel_handler,
            ("te", "tu",): self.__trades_channel_handler,
            ("fos", "fon", "fou", "foc",): self.__funding_offers_channel_handler,
            ("fcs", "fcn", "fcu", "fcc",): self.__funding_credits_channel_handler,
            ("fls", "fln", "flu", "flc",): self.__funding_loans_channel_handler,
            ("ws", "wu",): self.__wallets_channel_handler,
            ("bu",): self.__balance_info_channel_handler
        }

    def handle(self, type, stream):
        for abbreviations in self.__handlers.keys():
            if type in abbreviations:
                return self.__handlers[abbreviations](type, stream)
        
        if self.strict == True:
            raise BfxWebsocketException(f"Event of type <{type}> not found in self.__handlers.")

    def __orders_channel_handler(self, type, stream):
        _labels = [
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
        ]

        if type == "os":
            self.event_emitter.emit("order_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "on" or type == "ou" or type == "oc":
            self.event_emitter.emit({
                "on": "new_order",
                "ou": "order_update",
                "oc": "order_cancel"
            }[type], _label_stream_data(_labels, *stream))

    def __positions_channel_handler(self, type, stream):
        _labels = [
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
        ]

        if type == "ps":
            self.event_emitter.emit("position_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "pn" or type == "pu" or type == "pc":
            self.event_emitter.emit({
                "pn": "new_position",
                "pu": "position_update",
                "pc": "position_close"
            }[type], _label_stream_data(_labels, *stream))

    def __trades_channel_handler(self, type, stream):
        if type == "te":
            self.event_emitter.emit("trade_executed", _label_stream_data([
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
            ], *stream))

        if type == "tu":
            self.event_emitter.emit("trade_execution_update", _label_stream_data([
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
            ], *stream))

    def __funding_offers_channel_handler(self, type, stream):
        _labels = [
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
            "_PLACEHOLDER",
        ]

        if type == "fos":
            self.event_emitter.emit("funding_offer_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "fon" or type == "fou" or type == "foc":
            self.event_emitter.emit({
                "fon": "funding_offer_new",
                "fou": "funding_offer_update",
                "foc": "funding_offer_cancel"
            }[type], _label_stream_data(_labels, *stream))

    def __funding_credits_channel_handler(self, type, stream):
        _labels = [
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
        ]

        if type == "fcs":
            self.event_emitter.emit("funding_credit_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "fcn" or type == "fcu" or type == "fcc":
            self.event_emitter.emit({
                "fcn": "funding_credit_new",
                "fcu": "funding_credit_update",
                "fcc": "funding_credit_close"
            }[type], _label_stream_data(_labels, *stream))

    def __funding_loans_channel_handler(self, type, stream):
        _labels = [
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
        ]

        if type == "fls":
            self.event_emitter.emit("funding_loan_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "fln" or type == "flu" or type == "flc":
            self.event_emitter.emit({
                "fln": "funding_loan_new",
                "flu": "funding_loan_update",
                "flc": "funding_loan_close"
            }[type], _label_stream_data(_labels, *stream))

    def __wallets_channel_handler(self, type, stream):
        _labels = [
            "WALLET_TYPE", 
            "CURRENCY", 
            "BALANCE", 
            "UNSETTLED_INTEREST",
            "BALANCE_AVAILABLE",
            "DESCRIPTION",
            "META"
        ]

        if type == "ws":
            self.event_emitter.emit("wallet_snapshot", [ _label_stream_data(_labels, *substream) for substream in stream ])

        if type == "wu":
            self.event_emitter.emit("wallet_update", _label_stream_data(_labels, *stream))

    def __balance_info_channel_handler(self, type, stream):
        if type == "bu":
            self.event_emitter.emit("balance_update", _label_stream_data([
                "AUM",
                "AUM_NET"
            ], *stream))