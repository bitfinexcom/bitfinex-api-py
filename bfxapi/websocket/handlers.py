from enum import Enum

from .errors import BfxWebsocketException

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
            Channels.STATUS: self.__status_channel_handler,
        }

    def handle(self, subscription, *parameters):
        self.__handlers[subscription["channel"]](subscription, *parameters)

    def __ticker_channel_handler(self, subscription, *parameters):
        self.event_emitter.emit("ticker", subscription, parameters[0])

    def __trades_channel_handler(self, subscription, *parameters):
        if len(parameters) == 1:
            self.event_emitter.emit("trades_snapshot", subscription, parameters[0])

        if len(parameters) == 2:
            self.event_emitter.emit("trades_update", subscription, parameters[0], parameters[1])

    def __book_channel_handler(self, subscription, *parameters):
        if all(isinstance(element, list) for element in parameters[0]):
            self.event_emitter.emit("book_snapshot", subscription, parameters[0])
        else: self.event_emitter.emit("book_update", subscription, parameters[0])

    def __candles_channel_handler(self, subscription, *parameters):
        if all(isinstance(element, list) for element in parameters[0]):
            self.event_emitter.emit("candles_snapshot", subscription, parameters[0])
        else: self.event_emitter.emit("candles_update", subscription, parameters[0])

    def __status_channel_handler(self, subscription, *parameters):
        self.event_emitter.emit("status", subscription, parameters[0])

class AuthenticatedEventsHandler(object):
    def __init__(self, event_emitter, strict = False):
        self.event_emitter, self.strict = event_emitter, strict

        self.__handlers = {
            "bu": self.__bu_event_handler,
            "ws": self.__ws_event_handler,
            "wu": self.__wu_event_handler,
            "os": self.__os_event_handler,
            "on": self.__on_event_handler,
            "ou": self.__ou_event_handler,
            "oc": self.__oc_event_handler,
            "ps": self.__ps_event_handler,
            "pn": self.__pn_event_handler,
            "pu": self.__pu_event_handler,
            "pc": self.__pc_event_handler,
            "fos": self.__fos_event_handler,
            "fon": self.__fon_event_handler,
            "fou": self.__fou_event_handler,
            "foc": self.__foc_event_handler,
        }

    def handle(self, type, stream):
        if type in self.__handlers:
            self.__handlers[type](*stream)
        elif self.strict == True:
            raise BfxWebsocketException(f"Event of type <{type}> not found in self.__handlers.")

    def __bu_event_handler(self, *stream):
        self.event_emitter.emit("balance_update", _label_stream_data(
            [ 
                "AUM", 
                "AUM_NET" 
            ],
            *stream
        ))

    def __ws_event_handler(self, *stream):
        self.event_emitter.emit("wallet_snapshot", [
            _label_stream_data(
                [
                    "WALLET_TYPE", 
                    "CURRENCY", 
                    "BALANCE", 
                    "UNSETTLED_INTEREST", 
                    "BALANCE_AVAILABLE", 
                    "DESCRIPTION", 
                    "META"
                ],
                *substream
            ) for substream in stream
        ])
    
    def __wu_event_handler(self, *stream):
        self.event_emitter.emit("wallet_update", _label_stream_data(
            [
                "WALLET_TYPE", 
                "CURRENCY", 
                "BALANCE", 
                "UNSETTLED_INTEREST", 
                "BALANCE_AVAILABLE", 
                "DESCRIPTION", 
                "META"
            ],
            *stream
        ))

    def __os_event_handler(self, *stream):
        self.event_emitter.emit("order_snapshot", [
            _label_stream_data(
                [
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
                    "STATUS", 
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
                ],
                *substream
             ) for substream in stream
        ])

    def __on_event_handler(self, *stream):
        self.event_emitter.emit("new_order", _label_stream_data(
            [
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
                "_PLACEHOLDER"
            ],
            *stream
        ))

    def __ou_event_handler(self, *stream):
        self.event_emitter.emit("order_update", _label_stream_data(
            [
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
                "_PLACEHOLDER"
            ],
            *stream
        ))

    def __oc_event_handler(self, *stream):
        self.event_emitter.emit("order_cancel", _label_stream_data(
            [
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
                "_PLACEHOLDER"
            ],
            *stream
        ))

    def __ps_event_handler(self, *stream):
        self.event_emitter.emit("position_snapshot", [
            _label_stream_data(
                [
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
                ],
                *substream
            )
            for substream in stream
        ])

    def __pn_event_handler(self, *stream):
        self.event_emitter.emit("new_position", _label_stream_data(
            [
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
            ],
            *stream
        ))

    def __pu_event_handler(self, *stream):
        self.event_emitter.emit("position_update", _label_stream_data(
            [
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
            ],
            *stream
        ))

    def __pc_event_handler(self, *stream):
        self.event_emitter.emit("position_cancel", _label_stream_data(
            [
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
            ],
            *stream
        ))

    def __fos_event_handler(self, *stream):
        self.event_emitter.emit("funding_offer_snapshot", [
            _label_stream_data(
                [
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
                ],
                *substream
            )
            for substream in stream
        ])

    def __fon_event_handler(self, *stream):
        self.event_emitter.emit("funding_offer_new", _label_stream_data(
            [
                "ID",
                "SYMBOL",
                "MTS_CREATED",
                "MTS_UPDATED",
                "AMOUNT",
                "AMOUNT_ORIG",
                "TYPE",
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
                "RATE_REAL"
            ],
            *stream
        ))

    def __fou_event_handler(self, *stream):
        self.event_emitter.emit("funding_offer_update", _label_stream_data(
            [
                "ID",
                "SYMBOL",
                "MTS_CREATED",
                "MTS_UPDATED",
                "AMOUNT",
                "AMOUNT_ORIG",
                "TYPE",
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
                "RATE_REAL"
            ],
            *stream
        ))

    def __foc_event_handler(self, *stream):
        self.event_emitter.emit("funding_offer_cancel", _label_stream_data(
            [
                "ID",
                "SYMBOL",
                "MTS_CREATED",
                "MTS_UPDATED",
                "AMOUNT",
                "AMOUNT_ORIG",
                "TYPE",
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
                "RATE_REAL"
            ],
            *stream
        ))

def _label_stream_data(labels, *args, IGNORE = [ "_PLACEHOLDER" ]):
    if len(labels) != len(args):
        raise BfxWebsocketException("<labels> and <*args> arguments should contain the same amount of elements.")

    return { label: args[index] for index, label in enumerate(labels) if label not in IGNORE }