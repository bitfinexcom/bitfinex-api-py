from typing import TYPE_CHECKING, \
    Dict, Tuple, Any

from bfxapi.types import serializers

from bfxapi.types.serializers import _Notification

if TYPE_CHECKING:
    from bfxapi.types.dataclasses import \
        Order, FundingOffer

    from pyee.base import EventEmitter

class AuthEventsHandler:
    __ONCE_ABBREVIATIONS = {
        "os": "order_snapshot", "ps": "position_snapshot", "fos": "funding_offer_snapshot",
        "fcs": "funding_credit_snapshot", "fls": "funding_loan_snapshot", "ws": "wallet_snapshot"
    }

    __ON_ABBREVIATIONS = {
        "on": "order_new", "ou": "order_update", "oc": "order_cancel", 
        "pn": "position_new", "pu": "position_update", "pc": "position_close", 
        "fon": "funding_offer_new", "fou": "funding_offer_update", "foc": "funding_offer_cancel", 
        "fcn": "funding_credit_new", "fcu": "funding_credit_update", "fcc": "funding_credit_close",
        "fln": "funding_loan_new", "flu": "funding_loan_update", "flc": "funding_loan_close", 
        "te": "trade_execution", "tu": "trade_execution_update", "wu": "wallet_update"
    }

    __ABBREVIATIONS = {
        **__ONCE_ABBREVIATIONS,
        **__ON_ABBREVIATIONS
    }

    ONCE_EVENTS = [
        *list(__ONCE_ABBREVIATIONS.values())
    ]

    ON_EVENTS = [
        *list(__ON_ABBREVIATIONS.values()),
        "notification", "on-req-notification", "ou-req-notification", 
        "oc-req-notification", "fon-req-notification", "foc-req-notification"
    ]

    def __init__(self, event_emitter: "EventEmitter") -> None:
        self.__event_emitter = event_emitter

        self.__serializers: Dict[Tuple[str, ...], serializers._Serializer] = {
            ("os", "on", "ou", "oc",): serializers.Order,
            ("ps", "pn", "pu", "pc",): serializers.Position,
            ("te", "tu"): serializers.Trade,
            ("fos", "fon", "fou", "foc",): serializers.FundingOffer,
            ("fcs", "fcn", "fcu", "fcc",): serializers.FundingCredit,
            ("fls", "fln", "flu", "flc",): serializers.FundingLoan,
            ("ws", "wu",): serializers.Wallet
        }

    def handle(self, abbrevation: str, stream: Any) -> None:
        if abbrevation == "n":
            return self.__notification(stream)

        for abbrevations, serializer in self.__serializers.items():
            if abbrevation in abbrevations:
                event = AuthEventsHandler.__ABBREVIATIONS[abbrevation]

                if all(isinstance(sub_stream, list) for sub_stream in stream):
                    data = [ serializer.parse(*sub_stream) for sub_stream in stream ]
                else: data = serializer.parse(*stream)

                self.__event_emitter.emit(event, data)

                break

    def __notification(self, stream: Any) -> None:
        event: str = "notification"

        serializer: _Notification = _Notification[None](serializer=None)

        if stream[1] == "on-req" or stream[1] == "ou-req" or stream[1] == "oc-req":
            event, serializer = f"{stream[1]}-notification", \
                _Notification["Order"](serializer=serializers.Order)

        if stream[1] == "fon-req" or stream[1] == "foc-req":
            event, serializer = f"{stream[1]}-notification", \
                _Notification["FundingOffer"](serializer=serializers.FundingOffer)

        self.__event_emitter.emit(event, serializer.parse(*stream))
