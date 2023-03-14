from .. exceptions import BfxBaseException

__all__ = [
    "BfxWebsocketException",

    "ConnectionNotOpen",
    "TooManySubscriptions",
    "ZeroConnectionsError",
    "WebsocketAuthenticationRequired",
    "InvalidAuthenticationCredentials",
    "EventNotSupported",
    "HandlerNotFound",
    "OutdatedClientVersion"
]

class BfxWebsocketException(BfxBaseException):
    """
    Base class for all custom exceptions in bfxapi/websocket/exceptions.py.
    """

class ConnectionNotOpen(BfxWebsocketException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

class TooManySubscriptions(BfxWebsocketException):
    """
    This error indicates a subscription attempt after reaching the limit of simultaneous connections.
    """

class ZeroConnectionsError(BfxWebsocketException):
    """
    This error indicates an attempt to subscribe to a public channel while the number of connections is 0.
    """

class WebsocketAuthenticationRequired(BfxWebsocketException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

class InvalidAuthenticationCredentials(BfxWebsocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

class EventNotSupported(BfxWebsocketException):
    """
    This error indicates a failed attempt to subscribe to an event not supported by the BfxWebsocketClient.
    """


class HandlerNotFound(BfxWebsocketException):
    """
    This error indicates that a handler was not found for an incoming message.
    """

class OutdatedClientVersion(BfxWebsocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """
