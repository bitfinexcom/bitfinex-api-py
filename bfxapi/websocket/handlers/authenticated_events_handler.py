from ...types import serializers

from ...types.serializers import _Notification

class AuthenticatedEventsHandler:
    __once_abbreviations = {
        "os": "order_snapshot", "ps": "position_snapshot", "fos": "funding_offer_snapshot",
        "fcs": "funding_credit_snapshot", "fls": "funding_loan_snapshot", "ws": "wallet_snapshot"
    }

    __on_abbreviations = {
        "on": "order_new", "ou": "order_update", "oc": "order_cancel", 
        "pn": "position_new", "pu": "position_update", "pc": "position_close", 
        "fon": "funding_offer_new", "fou": "funding_offer_update", "foc": "funding_offer_cancel", 
        "fcn": "funding_credit_new", "fcu": "funding_credit_update", "fcc": "funding_credit_close",
        "fln": "funding_loan_new", "flu": "funding_loan_update", "flc": "funding_loan_close", 
        "te": "trade_execution", "tu": "trade_execution_update", "wu": "wallet_update"
    }

    __abbreviations = {
        **__once_abbreviations,
        **__on_abbreviations
    }

    __serializers = {
        ("os", "on", "ou", "oc",): serializers.Order,
        ("ps", "pn", "pu", "pc",): serializers.Position,
        ("te", "tu"): serializers.Trade,
        ("fos", "fon", "fou", "foc",): serializers.FundingOffer,
        ("fcs", "fcn", "fcu", "fcc",): serializers.FundingCredit,
        ("fls", "fln", "flu", "flc",): serializers.FundingLoan,
        ("ws", "wu",): serializers.Wallet
    }

    ONCE_EVENTS = [
        *list(__once_abbreviations.values())
    ]

    ON_EVENTS = [
        *list(__on_abbreviations.values()),
        "notification", "on-req-notification", "ou-req-notification", 
        "oc-req-notification", "fon-req-notification", "foc-req-notification"
    ]

    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

    def handle(self, abbrevation, stream):
        if abbrevation == "n":
            return self.__notification(stream)

        for abbrevations, serializer in AuthenticatedEventsHandler.__serializers.items():
            if abbrevation in abbrevations:
                event = AuthenticatedEventsHandler.__abbreviations[abbrevation]

                if all(isinstance(substream, list) for substream in stream):
                    return self.event_emitter.emit(event, [ serializer.parse(*substream) for substream in stream ])

                return self.event_emitter.emit(event, serializer.parse(*stream))

    def __notification(self, stream):
        event, serializer = "notification", _Notification(serializer=None)

        if stream[1] == "on-req" or stream[1] == "ou-req" or stream[1] == "oc-req":
            event, serializer = f"{stream[1]}-notification", _Notification(serializer=serializers.Order)

        if stream[1] == "fon-req" or stream[1] == "foc-req":
            event, serializer = f"{stream[1]}-notification", _Notification(serializer=serializers.FundingOffer)

        return self.event_emitter.emit(event, serializer.parse(*stream))
