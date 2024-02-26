class BfxBaseException(Exception):
    """
    Base class for every custom exception thrown by bitfinex-api-py.
    """


class IncompleteCredentialError(BfxBaseException):
    pass


class InvalidCredentialError(BfxBaseException):
    pass
