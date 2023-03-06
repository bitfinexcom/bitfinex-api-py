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

class ConnectionNotOpen(BfxWebsocketException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

class TooManySubscriptions(BfxWebsocketException):
    """
    This error indicates a subscription attempt after reaching the limit of simultaneous connections.
    """

class WebsocketAuthenticationRequired(BfxWebsocketException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

class EventNotSupported(BfxWebsocketException):
    """
    This error indicates a failed attempt to subscribe to an event not supported by the BfxWebsocketClient.
    """

class OutdatedClientVersion(BfxWebsocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """


class InvalidAuthenticationCredentials(BfxWebsocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """


class HandlerNotFound(BfxWebsocketException):
    """
    This error indicates that a handler was not found for an incoming message.
    """
