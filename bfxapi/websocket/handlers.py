from . import serializers
from .enums import Channels
from .exceptions import BfxWebsocketException

def _get_sub_dictionary(dictionary, keys):
    return { key: dictionary[key] for key in dictionary if key in keys }
    
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
        if channel := subscription["channel"] or channel in self.__handlers.keys():
            return self.__handlers[channel](subscription, *stream)

    def __ticker_channel_handler(self, subscription, *stream):
        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "t_ticker_update",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                serializers.TradingPairTicker.parse(*stream[0])
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "f_ticker_update",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                serializers.FundingCurrencyTicker.parse(*stream[0])
            )

    def __trades_channel_handler(self, subscription, *stream):
        if type := stream[0] or type in [ "te", "tu", "fte", "ftu" ]:
            if subscription["symbol"].startswith("t"):
                return self.event_emitter.emit(
                    { "te": "t_trade_executed", "tu": "t_trade_execution_update" }[type],
                    _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                    serializers.TradingPairTrade.parse(*stream[1])
                )

            if subscription["symbol"].startswith("f"):
                return self.event_emitter.emit(
                    { "fte": "f_trade_executed", "ftu": "f_trade_execution_update" }[type],
                    _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                    serializers.FundingCurrencyTrade.parse(*stream[1])
                )

        if subscription["symbol"].startswith("t"):
            return self.event_emitter.emit(
                "t_trades_snapshot",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "pair" ]),
                [ serializers.TradingPairTrade.parse(*substream) for substream in stream[0] ]
            )

        if subscription["symbol"].startswith("f"):
            return self.event_emitter.emit(
                "f_trades_snapshot",
                _get_sub_dictionary(subscription, [ "chanId", "symbol", "currency" ]),
                [ serializers.FundingCurrencyTrade.parse(*substream)  for substream in stream[0] ]
            )

    def __book_channel_handler(self, subscription, *stream):
        subscription = _get_sub_dictionary(subscription, [ "chanId", "symbol", "prec", "freq", "len", "subId", "pair" ])

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
        subscription = _get_sub_dictionary(subscription, [ "chanId", "key" ])

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
        subscription = _get_sub_dictionary(subscription, [ "chanId", "key" ])

        if subscription["key"].startswith("deriv:"):
            return self.event_emitter.emit(
                "derivatives_status_update",
                subscription,
                serializers.DerivativesStatus.parse(*stream[0])
            )

class AuthenticatedChannelsHandler(object):
    EVENTS = [
        "order_snapshot", "new_order", "order_update", "order_cancel",
        "position_snapshot", "new_position", "position_update", "position_close",
        "trade_executed", "trade_execution_update",
        "funding_offer_snapshot", "funding_offer_new", "funding_offer_update", "funding_offer_cancel",
        "funding_credit_snapshot", "funding_credit_new", "funding_credit_update", "funding_credit_close",
        "funding_loan_snapshot", "funding_loan_new", "funding_loan_update", "funding_loan_close",
        "wallet_snapshot", "wallet_update",
        "balance_update",
    ]

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
        if type == "os":
            return self.event_emitter.emit("order_snapshot", [ 
                serializers.Order.parse(*substream) for substream in stream 
            ])

        if type in [ "on", "ou", "oc" ]:
            return self.event_emitter.emit({
                "on": "new_order",
                "ou": "order_update",
                "oc": "order_cancel"
            }[type], serializers.Order.parse(*stream))

    def __positions_channel_handler(self, type, stream):
        if type == "ps":
            return self.event_emitter.emit("position_snapshot", [ 
                serializers.Position.parse(*substream) for substream in stream 
            ])

        if type in [ "pn", "pu", "pc" ]:
            return self.event_emitter.emit({
                "pn": "new_position",
                "pu": "position_update",
                "pc": "position_close"
            }[type], serializers.Position.parse(*stream))

    def __trades_channel_handler(self, type, stream):
        if type == "te":
            self.event_emitter.emit("trade_executed", serializers.TradeExecuted.parse(*stream))

        if type == "tu":
            self.event_emitter.emit("trade_execution_update", serializers.TradeExecutionUpdate.parse(*stream))

    def __funding_offers_channel_handler(self, type, stream):
        if type == "fos":
            return self.event_emitter.emit("funding_offer_snapshot", [ 
                serializers.FundingOffer.parse(*substream) for substream in stream 
            ])

        if type in [ "fon", "fou", "foc" ]:
            return self.event_emitter.emit({
                "fon": "funding_offer_new",
                "fou": "funding_offer_update",
                "foc": "funding_offer_cancel"
            }[type], serializers.FundingOffer.parse(*stream))

    def __funding_credits_channel_handler(self, type, stream):
        if type == "fcs":
            return self.event_emitter.emit("funding_credit_snapshot", [ 
                serializers.FundingCredit.parse(*substream) for substream in stream 
            ])

        if type in [ "fcn", "fcu", "fcc" ]:
            return self.event_emitter.emit({
                "fcn": "funding_credit_new",
                "fcu": "funding_credit_update",
                "fcc": "funding_credit_close"
            }[type], serializers.FundingCredit.parse(*stream))

    def __funding_loans_channel_handler(self, type, stream):
        if type == "fls":
            return self.event_emitter.emit("funding_loan_snapshot", [ 
                serializers.FundingLoan.parse(*substream) for substream in stream 
            ])

        if type in [ "fln", "flu", "flc" ]:
            return self.event_emitter.emit({
                "fln": "funding_loan_new",
                "flu": "funding_loan_update",
                "flc": "funding_loan_close"
            }[type], serializers.FundingLoan.parse(*stream))

    def __wallets_channel_handler(self, type, stream):
        if type == "ws":
            return self.event_emitter.emit("wallet_snapshot", [ 
                serializers.Wallet.parse(*substream) for substream in stream 
            ])

        if type == "wu":
            return self.event_emitter.emit("wallet_update", serializers.Wallet.parse(*stream))

    def __balance_info_channel_handler(self, type, stream):
        if type == "bu":
            return self.event_emitter.emit("balance_update", serializers.BalanceInfo.parse(*stream))