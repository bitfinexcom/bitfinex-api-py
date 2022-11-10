from enum import Enum

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
    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

        self.__handlers = {
            "bu": self.__bu_event_handler,
            "ws": self.__ws_event_handler,
            "wu": self.__wu_event_handler,
            "os": self.__os_event_handler,
            "on": self.__on_event_handler
        }

    def handle(self, type, parameters):
        if type in self.__handlers:
            self.__handlers[type](*parameters)

    def __bu_event_handler(self, *parameters):
        self.event_emitter.emit("balance_update", _label_array_elements(
            [ 
                "AUM", 
                "AUM_NET" 
            ],
            *parameters
        ))

    def __ws_event_handler(self, *parameters):
        self.event_emitter.emit("wallet_snapshot", [
            _label_array_elements(
                [
                    "WALLET_TYPE", 
                    "CURRENCY", 
                    "BALANCE", 
                    "UNSETTLED_INTEREST", 
                    "BALANCE_AVAILABLE", 
                    "DESCRIPTION", 
                    "META"
                ],
                *parameter
            ) for parameter in parameters
        ])
    
    def __wu_event_handler(self, *parameters):
        self.event_emitter.emit("wallet_update", _label_array_elements(
            [
                "WALLET_TYPE", 
                "CURRENCY", 
                "BALANCE", 
                "UNSETTLED_INTEREST", 
                "BALANCE_AVAILABLE", 
                "DESCRIPTION", 
                "META"
            ],
            *parameters
        ))

    def __os_event_handler(self, *parameters):
        self.event_emitter.emit("order_snapshot", [
            _label_array_elements(
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
                *parameter
             ) for parameter in parameters
        ])

    def __on_event_handler(self, *parameters):
        self.event_emitter.emit("new_order", _label_array_elements(
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
            *parameters
        ))

def _label_array_elements(labels, *args):
    if len(labels) != len(args):
        raise Exception("<labels> and <*args> arguments should contain the same amount of elements.")

    _PLACEHOLDER = "_PLACEHOLDER"

    return { label: args[index] for index, label in enumerate(labels) if label != _PLACEHOLDER }