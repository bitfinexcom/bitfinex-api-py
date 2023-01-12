from .. exceptions import BfxBaseException

__all__ = [
    "BfxWebsocketException",

    "ConnectionNotOpen",
    "TooManySubscriptions",
    "WebsocketAuthenticationRequired",
    "InvalidAuthenticationCredentials",
    "EventNotSupported",
    "OutdatedClientVersion"
]

class BfxWebsocketException(BfxBaseException):
    """
    Base class for all custom exceptions in bfxapi/websocket/exceptions.py.
    """

    pass

class ConnectionNotOpen(BfxWebsocketException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

    pass

class TooManySubscriptions(BfxWebsocketException):
    """
    This error indicates an attempt to subscribe to a public channel after reaching the limit of simultaneous connections.
    """

    pass

class WebsocketAuthenticationRequired(BfxWebsocketException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

    pass

class EventNotSupported(BfxWebsocketException):
    """
    This error indicates a failed attempt to subscribe to an event not supported by the BfxWebsocketClient.
    """

    pass

class OutdatedClientVersion(BfxWebsocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """

    pass

class InvalidAuthenticationCredentials(BfxWebsocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

    pass