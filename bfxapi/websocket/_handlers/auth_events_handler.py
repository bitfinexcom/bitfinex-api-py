from typing import Any, Dict, Tuple

from pyee.base import EventEmitter

from bfxapi.types import serializers
from bfxapi.types.dataclasses import FundingOffer, Order
from bfxapi.types.serializers import _Notification


class AuthEventsHandler:
    __ABBREVIATIONS = {
        "os": "order_snapshot",
        "on": "order_new",
        "ou": "order_update",
        "oc": "order_cancel",
        "ps": "position_snapshot",
        "pn": "position_new",
        "pu": "position_update",
        "pc": "position_close",
        "te": "trade_execution",
        "tu": "trade_execution_update",
        "fos": "funding_offer_snapshot",
        "fon": "funding_offer_new",
        "fou": "funding_offer_update",
        "foc": "funding_offer_cancel",
        "fcs": "funding_credit_snapshot",
        "fcn": "funding_credit_new",
        "fcu": "funding_credit_update",
        "fcc": "funding_credit_close",
        "fls": "funding_loan_snapshot",
        "fln": "funding_loan_new",
        "flu": "funding_loan_update",
        "flc": "funding_loan_close",
        "ws": "wallet_snapshot",
        "wu": "wallet_update",
        "fiu": "funding_info_update",
        "bu": "balance_update",
    }

    __SERIALIZERS: Dict[Tuple[str, ...], serializers._Serializer] = {
        ("os", "on", "ou", "oc"): serializers.Order,
        ("ps", "pn", "pu", "pc"): serializers.Position,
        ("te", "tu"): serializers.Trade,
        ("fos", "fon", "fou", "foc"): serializers.FundingOffer,
        ("fcs", "fcn", "fcu", "fcc"): serializers.FundingCredit,
        ("fls", "fln", "flu", "flc"): serializers.FundingLoan,
        ("ws", "wu"): serializers.Wallet,
        ("fiu",): serializers.FundingInfo,
        ("bu",): serializers.BalanceInfo,
    }

    def __init__(self, event_emitter: EventEmitter) -> None:
        self.__event_emitter = event_emitter

    def handle(self, abbrevation: str, stream: Any) -> None:
        if abbrevation == "n":
            self.__notification(stream)
        elif abbrevation == "miu":
            if stream[0] == "base":
                self.__event_emitter.emit(
                    "base_margin_info", serializers.BaseMarginInfo.parse(*stream)
                )
            elif stream[0] == "sym":
                self.__event_emitter.emit(
                    "symbol_margin_info", serializers.SymbolMarginInfo.parse(*stream)
                )
        else:
            for abbrevations, serializer in AuthEventsHandler.__SERIALIZERS.items():
                if abbrevation in abbrevations:
                    event = AuthEventsHandler.__ABBREVIATIONS[abbrevation]

                    if all(isinstance(sub_stream, list) for sub_stream in stream):
                        data = [serializer.parse(*sub_stream) for sub_stream in stream]
                    else:
                        data = serializer.parse(*stream)

                    self.__event_emitter.emit(event, data)

    def __notification(self, stream: Any) -> None:
        event: str = "notification"

        serializer: _Notification = _Notification[None](serializer=None)

        if stream[1] in ("on-req", "ou-req", "oc-req"):
            event, serializer = f"{stream[1]}-notification", _Notification[Order](
                serializer=serializers.Order
            )

        if stream[1] in ("fon-req", "foc-req"):
            event, serializer = f"{stream[1]}-notification", _Notification[
                FundingOffer
            ](serializer=serializers.FundingOffer)

        self.__event_emitter.emit(event, serializer.parse(*stream))
