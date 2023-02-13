from ..types import *

from .. import serializers

from ..enums import Channels

class PublicChannelsHandler(object):
    EVENTS = [
        "t_ticker_update", "f_ticker_update",
        "t_trade_executed", "t_trade_execution_update", "f_trade_executed", "f_trade_execution_update", "t_trades_snapshot", "f_trades_snapshot",
        "t_book_snapshot", "f_book_snapshot", "t_raw_book_snapshot", "f_raw_book_snapshot", "t_book_update", "f_book_update", "t_raw_book_update", "f_raw_book_update",
        "candles_snapshot", "candles_update",
        "derivatives_status_update",
    ]

    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

        self.__handlers = {
            Channels.TICKER: self.__ticker_channel_handler,
            Channels.TRADES: self.__trades_channel_handler,
            Channels.BOOK: self.__book_channel_handler,
            Channels.CANDLES: self.__candles_channel_handler,
            Channels.STATUS: self.__status_channel_handler
        }

    def handle(self, subscription, *stream):
        _clear = lambda dictionary, *args: { key: value for key, value in dictionary.items() if key not in args }

        if channel := subscription["channel"] or channel in self.__handlers.keys():
            return self.__handlers[channel](_clear(subscription, "event", "channel", "subId"), *stream)

    def __ticker_channel_handler(self, subscription, *stream):
        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "t_ticker_update",
                subscription,
                serializers.TradingPairTicker.parse(*stream[0])
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "f_ticker_update",
                subscription,
                serializers.FundingCurrencyTicker.parse(*stream[0])
            )

    def __trades_channel_handler(self, subscription, *stream):
        if type := stream[0] or type in [ "te", "tu", "fte", "ftu" ]:
            if subscription["symbol"].startswith("t"):
                return self.event_emitter.emit(
                    { "te": "t_trade_executed", "tu": "t_trade_execution_update" }[type],
                    subscription,
                    serializers.TradingPairTrade.parse(*stream[1])
                )

            if subscription["symbol"].startswith("f"):
                return self.event_emitter.emit(
                    { "fte": "f_trade_executed", "ftu": "f_trade_execution_update" }[type],
                    subscription,
                    serializers.FundingCurrencyTrade.parse(*stream[1])
                )

        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "t_trades_snapshot",
                subscription,
                [ serializers.TradingPairTrade.parse(*substream) for substream in stream[0] ]
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "f_trades_snapshot",
                subscription,
                [ serializers.FundingCurrencyTrade.parse(*substream)  for substream in stream[0] ]
            )

    def __book_channel_handler(self, subscription, *stream):
        type = subscription["symbol"][0]

        if subscription["prec"] == "R0":
            _trading_pair_serializer, _funding_currency_serializer, IS_RAW_BOOK = serializers.TradingPairRawBook, serializers.FundingCurrencyRawBook, True
        else: _trading_pair_serializer, _funding_currency_serializer, IS_RAW_BOOK = serializers.TradingPairBook, serializers.FundingCurrencyBook, False

        if all(isinstance(substream, list) for substream in stream[0]):
            return self.event_emitter.emit(               
                type + "_" + (IS_RAW_BOOK and "raw_book" or "book") + "_snapshot",
                subscription, 
                [ { "t": _trading_pair_serializer, "f": _funding_currency_serializer }[type].parse(*substream) for substream in stream[0] ]
            )

        return self.event_emitter.emit(
            type + "_" + (IS_RAW_BOOK and "raw_book" or "book") + "_update",
            subscription, 
            { "t": _trading_pair_serializer, "f": _funding_currency_serializer }[type].parse(*stream[0])
        )
        
    def __candles_channel_handler(self, subscription, *stream):
        if all(isinstance(substream, list) for substream in stream[0]):
            return self.event_emitter.emit(
                "candles_snapshot", 
                subscription, 
                [ serializers.Candle.parse(*substream) for substream in stream[0] ]
            )

        return self.event_emitter.emit(
            "candles_update", 
            subscription, 
            serializers.Candle.parse(*stream[0])
        )

    def __status_channel_handler(self, subscription, *stream):
        if subscription["key"].startswith("deriv:"):
            return self.event_emitter.emit(
                "derivatives_status_update",
                subscription,
                serializers.DerivativesStatus.parse(*stream[0])
            )