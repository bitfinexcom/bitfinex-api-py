from typing import TYPE_CHECKING, \
    Union, List, Any, cast

from bfxapi.types import serializers

if TYPE_CHECKING:
    from bfxapi.websocket.subscriptions import Subscription, \
        Ticker, Trades, Book, Candles, Status

    from pyee.base import EventEmitter

    _NoHeaderSubscription = \
        Union[Ticker, Trades, Book, Candles, Status]

_CHECKSUM = "cs"

class PublicChannelsHandler:
    ONCE_PER_SUBSCRIPTION = [
        "t_trades_snapshot", "f_trades_snapshot", "t_book_snapshot", 
        "f_book_snapshot", "t_raw_book_snapshot", "f_raw_book_snapshot", 
        "candles_snapshot"
    ]

    EVENTS = [
        *ONCE_PER_SUBSCRIPTION,
        "t_ticker_update", "f_ticker_update", "t_trade_execution", 
        "t_trade_execution_update", "f_trade_execution", "f_trade_execution_update", 
        "t_book_update", "f_book_update", "t_raw_book_update", 
        "f_raw_book_update", "candles_update", "derivatives_status_update",
        "liquidation_feed_update",

        "checksum"
    ]

    def __init__(self, event_emitter: "EventEmitter") -> None:
        self.__event_emitter = event_emitter

    def handle(self, subscription: "Subscription", stream: List[Any]) -> None:
        def _strip(subscription: "Subscription", *args: str) -> "_NoHeaderSubscription":
            return cast("_NoHeaderSubscription", \
                { key: value for key, value in subscription.items() if key not in args })

        _subscription = _strip(subscription, "event", "channel", "chanId")

        if subscription["channel"] == "ticker":
            self.__ticker_channel_handler(cast("Ticker", _subscription), stream)
        elif subscription["channel"] == "trades":
            self.__trades_channel_handler(cast("Trades", _subscription), stream)
        elif subscription["channel"] == "book":
            _subscription = cast("Book", _subscription)

            if stream[0] == _CHECKSUM:
                self.__checksum_handler(_subscription, stream[1])
            else:
                if _subscription["prec"] != "R0":
                    self.__book_channel_handler(_subscription, stream)
                else:
                    self.__raw_book_channel_handler(_subscription, stream)
        elif subscription["channel"] == "candles":
            self.__candles_channel_handler(cast("Candles", _subscription), stream)
        elif subscription["channel"] == "status":
            self.__status_channel_handler(cast("Status", _subscription), stream)

    def __ticker_channel_handler(self, subscription: "Ticker", stream: List[Any]):
        if subscription["symbol"].startswith("t"):
            return self.__event_emitter.emit("t_ticker_update", subscription, \
                serializers.TradingPairTicker.parse(*stream[0]))

        if subscription["symbol"].startswith("f"):
            return self.__event_emitter.emit("f_ticker_update", subscription, \
                serializers.FundingCurrencyTicker.parse(*stream[0]))

    def __trades_channel_handler(self, subscription: "Trades", stream: List[Any]):
        if (event := stream[0]) and event in [ "te", "tu", "fte", "ftu" ]:
            events = { "te": "t_trade_execution", "tu": "t_trade_execution_update", \
                "fte": "f_trade_execution", "ftu": "f_trade_execution_update" }

            if subscription["symbol"].startswith("t"):
                return self.__event_emitter.emit(events[event], subscription, \
                    serializers.TradingPairTrade.parse(*stream[1]))

            if subscription["symbol"].startswith("f"):
                return self.__event_emitter.emit(events[event], subscription, \
                    serializers.FundingCurrencyTrade.parse(*stream[1]))

        if subscription["symbol"].startswith("t"):
            return self.__event_emitter.emit("t_trades_snapshot", subscription, \
                [ serializers.TradingPairTrade.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

        if subscription["symbol"].startswith("f"):
            return self.__event_emitter.emit("f_trades_snapshot", subscription, \
                [ serializers.FundingCurrencyTrade.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

    def __book_channel_handler(self, subscription: "Book", stream: List[Any]):
        if subscription["symbol"].startswith("t"):
            if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
                return self.__event_emitter.emit("t_book_snapshot", subscription, \
                    [ serializers.TradingPairBook.parse(*sub_stream) \
                        for sub_stream in stream[0] ])

            return self.__event_emitter.emit("t_book_update", subscription, \
                serializers.TradingPairBook.parse(*stream[0]))

        if subscription["symbol"].startswith("f"):
            if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
                return self.__event_emitter.emit("f_book_snapshot", subscription, \
                    [ serializers.FundingCurrencyBook.parse(*sub_stream) \
                        for sub_stream in stream[0] ])

            return self.__event_emitter.emit("f_book_update", subscription, \
                serializers.FundingCurrencyBook.parse(*stream[0]))

    def __raw_book_channel_handler(self, subscription: "Book", stream: List[Any]):
        if subscription["symbol"].startswith("t"):
            if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
                return self.__event_emitter.emit("t_raw_book_snapshot", subscription, \
                    [ serializers.TradingPairRawBook.parse(*sub_stream) \
                        for sub_stream in stream[0] ])

            return self.__event_emitter.emit("t_raw_book_update", subscription, \
                serializers.TradingPairRawBook.parse(*stream[0]))

        if subscription["symbol"].startswith("f"):
            if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
                return self.__event_emitter.emit("f_raw_book_snapshot", subscription, \
                    [ serializers.FundingCurrencyRawBook.parse(*sub_stream) \
                        for sub_stream in stream[0] ])

            return self.__event_emitter.emit("f_raw_book_update", subscription, \
                serializers.FundingCurrencyRawBook.parse(*stream[0]))

    def __candles_channel_handler(self, subscription: "Candles", stream: List[Any]):
        if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
            return self.__event_emitter.emit("candles_snapshot", subscription, \
                [ serializers.Candle.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

        return self.__event_emitter.emit("candles_update", subscription, \
            serializers.Candle.parse(*stream[0]))

    def __status_channel_handler(self, subscription: "Status", stream: List[Any]):
        if subscription["key"].startswith("deriv:"):
            return self.__event_emitter.emit("derivatives_status_update", subscription, \
                serializers.DerivativesStatus.parse(*stream[0]))

        if subscription["key"].startswith("liq:"):
            return self.__event_emitter.emit("liquidation_feed_update", subscription, \
               serializers.Liquidation.parse(*stream[0][0]))

    def __checksum_handler(self, subscription: "Book", value: int):
        return self.__event_emitter.emit("checksum", subscription, value)
