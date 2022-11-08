from .channels import Channels

class Manager(object):
    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

        self.__handlers = {
            Channels.TICKER: self.__ticker_channel_handler,
            Channels.TRADES: self.__trades_channel_handler,
            Channels.BOOK: self.__book_channel_handler
        }

    def handle(self, subscription, *parameters):
        return self.__handlers[subscription["channel"]](subscription, *parameters)

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