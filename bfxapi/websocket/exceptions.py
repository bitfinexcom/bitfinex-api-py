from bfxapi.exceptions import BfxBaseException


class ConnectionNotOpen(BfxBaseException):
    pass


class ActionRequiresAuthentication(BfxBaseException):
    pass


class ReconnectionTimeoutError(BfxBaseException):
    pass


class VersionMismatchError(BfxBaseException):
    pass


class SubIdError(BfxBaseException):
    pass


class UnknownChannelError(BfxBaseException):
    pass


class UnknownEventError(BfxBaseException):
    pass


class UnknownSubscriptionError(BfxBaseException):
    pass
