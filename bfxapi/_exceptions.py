class BfxBaseException(Exception):
    """
    Base class for every custom exception in bfxapi/rest/exceptions.py and bfxapi/websocket/exceptions.py.
    """

class IncompleteCredentialError(BfxBaseException):
    """
    This error indicates an incomplete credential object (missing api-key or api-secret).
    """

class InvalidCredentialError(BfxBaseException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """
