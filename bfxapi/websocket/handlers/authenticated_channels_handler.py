from typing import List

from ..types import *

from .. import serializers

from ..exceptions import BfxWebsocketException

class AuthenticatedChannelsHandler(object):
    __abbreviations = {
        "os": "order_snapshot", "on": "order_new", "ou": "order_update", "oc": "order_cancel",
        "ps": "position_snapshot", "pn": "position_new", "pu": "position_update", "pc": "position_close",
        "te": "trade_executed", "tu": "trade_execution_update",
        "fos": "funding_offer_snapshot", "fon": "funding_offer_new", "fou": "funding_offer_update", "foc": "funding_offer_cancel",
        "fcs": "funding_credit_snapshot", "fcn": "funding_credit_new", "fcu": "funding_credit_update", "fcc": "funding_credit_close",
        "fls": "funding_loan_snapshot", "fln": "funding_loan_new", "flu": "funding_loan_update", "flc": "funding_loan_close",
        "ws": "wallet_snapshot", "wu": "wallet_update",
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

    def __init__(self, event_emitter, strict = False):
        self.event_emitter, self.strict = event_emitter, strict

    def handle(self, type, stream):
        if type == "n":
            return self.__notification(stream)

        for types, serializer in AuthenticatedChannelsHandler.__serializers.items():
            if type in types:
                event = AuthenticatedChannelsHandler.__abbreviations[type]

                if all(isinstance(substream, list) for substream in stream):
                    return self.event_emitter.emit(event, [ serializer.parse(*substream) for substream in stream ])

                return self.event_emitter.emit(event, serializer.parse(*stream))
        
        if self.strict == True:
            raise BfxWebsocketException(f"Event of type <{type}> not found in self.__handlers.")
    
    def __notification(self, stream):
        type, serializer = "notification", serializers._Notification(serializer=None)

        if stream[1] == "on-req" or stream[1] == "ou-req" or stream[1] == "oc-req":
            type, serializer = f"{stream[1]}-notification", serializers._Notification[Order](serializer=serializers.Order)

        if stream[1] == "oc_multi-req":
            type, serializer = f"{stream[1]}-notification", serializers._Notification[List[Order]](serializer=serializers.Order, iterate=True)

        if stream[1] == "fon-req" or stream[1] == "foc-req":
            type, serializer = f"{stream[1]}-notification", serializers._Notification[FundingOffer](serializer=serializers.FundingOffer)

        return self.event_emitter.emit(type, serializer.parse(*stream))