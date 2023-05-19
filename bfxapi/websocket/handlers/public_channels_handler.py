from typing import TYPE_CHECKING, \
    Union, Dict, List, Any, cast

from bfxapi.types import serializers

if TYPE_CHECKING:
    from bfxapi.websocket.subscriptions import Subscription, \
        Ticker, Trades, Book, Candles, Status

    from pyee.base import EventEmitter

    _NoHeaderSubscription = \
        Union[Ticker, Trades, Book, Candles, Status]

class PublicChannelsHandler:
    ONCE_PER_SUBSCRIPTION_EVENTS = [
        "t_trades_snapshot", "f_trades_snapshot", "t_book_snapshot", 
        "f_book_snapshot", "t_raw_book_snapshot", "f_raw_book_snapshot", 
        "candles_snapshot"
    ]

    EVENTS = [
        *ONCE_PER_SUBSCRIPTION_EVENTS,
        "t_ticker_update", "f_ticker_update", "t_trade_execution", 
        "t_trade_execution_update", "f_trade_execution", "f_trade_execution_update", 
        "t_book_update", "f_book_update", "t_raw_book_update", 
        "f_raw_book_update", "candles_update", "derivatives_status_update"
    ]

    def __init__(self,
                 event_emitter: "EventEmitter",
                 events_per_subscription: Dict[str, List[str]]) -> None:
        self.__event_emitter, self.__events_per_subscription = \
            event_emitter, events_per_subscription

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
            self.__book_channel_handler(cast("Book", _subscription), stream)
        elif subscription["channel"] == "candles":
            self.__candles_channel_handler(cast("Candles", _subscription), stream)
        elif subscription["channel"] == "status":
            self.__status_channel_handler(cast("Status", _subscription), stream)

    def __emit(self, event: str, subscription: "_NoHeaderSubscription", data: Any) -> None:
        sub_id, should_emit_event = subscription["subId"], True

        if event in PublicChannelsHandler.ONCE_PER_SUBSCRIPTION_EVENTS:
            if sub_id not in self.__events_per_subscription:
                self.__events_per_subscription[sub_id] = [ event ]
            elif event not in self.__events_per_subscription[sub_id]:
                self.__events_per_subscription[sub_id] += [ event ]
            else: should_emit_event = False

        if should_emit_event:
            self.__event_emitter.emit(event, subscription, data)

    def __ticker_channel_handler(self, subscription: "Ticker", stream: List[Any]) -> None:
        if subscription["symbol"].startswith("t"):
            return self.__emit("t_ticker_update", subscription, \
                serializers.TradingPairTicker.parse(*stream[0]))

        if subscription["symbol"].startswith("f"):
            return self.__emit("f_ticker_update", subscription, \
                serializers.FundingCurrencyTicker.parse(*stream[0]))

    def __trades_channel_handler(self, subscription: "Trades", stream: List[Any]) -> None:
        if (event := stream[0]) and event in [ "te", "tu", "fte", "ftu" ]:
            events = { "te": "t_trade_execution", "tu": "t_trade_execution_update", \
                "fte": "f_trade_execution", "ftu": "f_trade_execution_update" }

            if subscription["symbol"].startswith("t"):
                return self.__emit(events[event], subscription, \
                    serializers.TradingPairTrade.parse(*stream[1]))

            if subscription["symbol"].startswith("f"):
                return self.__emit(events[event], subscription, \
                    serializers.FundingCurrencyTrade.parse(*stream[1]))

        if subscription["symbol"].startswith("t"):
            return self.__emit("t_trades_snapshot", subscription, \
                [ serializers.TradingPairTrade.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

        if subscription["symbol"].startswith("f"):
            return self.__emit("f_trades_snapshot", subscription, \
                [ serializers.FundingCurrencyTrade.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

    def __book_channel_handler(self, subscription: "Book", stream: List[Any]) -> None:
        t_or_f = subscription["symbol"][0]

        is_raw_book = subscription["prec"] == "R0"

        serializer = {
            "t": is_raw_book and serializers.TradingPairRawBook \
                or serializers.TradingPairBook,
            "f": is_raw_book and serializers.FundingCurrencyRawBook \
                or serializers.FundingCurrencyBook
        }[t_or_f]

        if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
            event = t_or_f + "_" + \
                (is_raw_book and "raw_book" or "book") + "_snapshot"

            return self.__emit(event, subscription, \
                [ serializer.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

        event = t_or_f + "_" + \
            (is_raw_book and "raw_book" or "book") + "_update"

        return self.__emit(event, subscription, \
            serializer.parse(*stream[0]))

    def __candles_channel_handler(self, subscription: "Candles", stream: List[Any]) -> None:
        if all(isinstance(sub_stream, list) for sub_stream in stream[0]):
            return self.__emit("candles_snapshot", subscription, \
                [ serializers.Candle.parse(*sub_stream) \
                    for sub_stream in stream[0] ])

        return self.__emit("candles_update", subscription, \
            serializers.Candle.parse(*stream[0]))

    def __status_channel_handler(self, subscription: "Status", stream: List[Any]) -> None:
        if subscription["key"].startswith("deriv:"):
            return self.__emit("derivatives_status_update", subscription, \
                serializers.DerivativesStatus.parse(*stream[0]))
