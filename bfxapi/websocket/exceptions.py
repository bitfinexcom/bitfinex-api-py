from ..exceptions import BfxBaseException

__all__ = [
    "BfxWebSocketException",

    "ConnectionNotOpen",
    "TooManySubscriptions",
    "ZeroConnectionsError",
    "ReconnectionTimeoutError",
    "WebSocketAuthenticationRequired",
    "InvalidAuthenticationCredentials",
    "EventNotSupported",
    "OutdatedClientVersion"
]

class BfxWebSocketException(BfxBaseException):
    """
    Base class for all custom exceptions in bfxapi/websocket/exceptions.py.
    """

class ConnectionNotOpen(BfxWebSocketException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

class TooManySubscriptions(BfxWebSocketException):
    """
    This error indicates a subscription attempt after reaching the limit of simultaneous connections.
    """

class ZeroConnectionsError(BfxWebSocketException):
    """
    This error indicates an attempt to subscribe to a public channel while the number of connections is 0.
    """

class ReconnectionTimeoutError(BfxWebSocketException):
    """
    This error indicates that the connection has been offline for too long without being able to reconnect.
    """

class WebSocketAuthenticationRequired(BfxWebSocketException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

class InvalidAuthenticationCredentials(BfxWebSocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

class EventNotSupported(BfxWebSocketException):
    """
    This error indicates a failed attempt to subscribe to an event not supported by the BfxWebSocketClient.
    """

class OutdatedClientVersion(BfxWebSocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """
