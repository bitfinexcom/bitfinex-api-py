from .. import serializers

from .. serializers import _Notification

from .. exceptions import HandlerNotFound

class AuthenticatedChannelsHandler:
    __abbreviations = {
        "os": "order_snapshot", "on": "order_new", "ou": "order_update", 
        "oc": "order_cancel", "ps": "position_snapshot", "pn": "position_new", 
        "pu": "position_update", "pc": "position_close", "te": "trade_executed", 
        "tu": "trade_execution_update", "fos": "funding_offer_snapshot", "fon": "funding_offer_new", 
        "fou": "funding_offer_update", "foc": "funding_offer_cancel", "fcs": "funding_credit_snapshot", 
        "fcn": "funding_credit_new", "fcu": "funding_credit_update", "fcc": "funding_credit_close",
        "fls": "funding_loan_snapshot", "fln": "funding_loan_new", "flu": "funding_loan_update", 
        "flc": "funding_loan_close", "ws": "wallet_snapshot", "wu": "wallet_update",
        "bu": "balance_update",
    }

    __serializers = {
        ("os", "on", "ou", "oc",): serializers.Order,
        ("ps", "pn", "pu", "pc",): serializers.Position,
        ("te", "tu"): serializers.Trade,
        ("fos", "fon", "fou", "foc",): serializers.FundingOffer,
        ("fcs", "fcn", "fcu", "fcc",): serializers.FundingCredit,
        ("fls", "fln", "flu", "flc",): serializers.FundingLoan,
        ("ws", "wu",): serializers.Wallet,
        ("bu",): serializers.Balance
    }

    EVENTS = [
        "notification", 
        "on-req-notification", "ou-req-notification", "oc-req-notification",
        "oc_multi-notification",
        "fon-req-notification", "foc-req-notification",
        *list(__abbreviations.values())
    ]

    def __init__(self, event_emitter):
        self.event_emitter = event_emitter

    def handle(self, abbrevation, stream):
        if abbrevation == "n":
            return self.__notification(stream)

        for abbrevations, serializer in AuthenticatedChannelsHandler.__serializers.items():
            if abbrevation in abbrevations:
                event = AuthenticatedChannelsHandler.__abbreviations[abbrevation]

                if all(isinstance(substream, list) for substream in stream):
                    return self.event_emitter.emit(event, [ serializer.parse(*substream) for substream in stream ])

                return self.event_emitter.emit(event, serializer.parse(*stream))

        raise HandlerNotFound(f"No handler found for event of type <{abbrevation}>.")

    def __notification(self, stream):
        event, serializer = "notification", _Notification(serializer=None)

        if stream[1] == "on-req" or stream[1] == "ou-req" or stream[1] == "oc-req":
            event, serializer = f"{stream[1]}-notification", _Notification(serializer=serializers.Order)

        if stream[1] == "oc_multi-req":
            event, serializer = f"{stream[1]}-notification", _Notification(serializer=serializers.Order, iterate=True)

        if stream[1] == "fon-req" or stream[1] == "foc-req":
            event, serializer = f"{stream[1]}-notification", _Notification(serializer=serializers.FundingOffer)

        return self.event_emitter.emit(event, serializer.parse(*stream))
