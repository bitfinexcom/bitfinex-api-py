from ..exceptions import BfxBaseException

__all__ = [
    "BfxWebSocketException",

    "ConnectionNotOpen",
    "FullBucketError",
    "ZeroConnectionsError",
    "ReconnectionTimeoutError",
    "ActionRequiresAuthentication",
    "InvalidAuthenticationCredentials",
    "UnknownChannelError",
    "UnknownEventError",
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

class FullBucketError(BfxWebSocketException):
    """
    Thrown when a user attempts a subscription but all buckets are full.
    """

class ZeroConnectionsError(BfxWebSocketException):
    """
    This error indicates an attempt to subscribe to a public channel while the number of connections is 0.
    """

class ReconnectionTimeoutError(BfxWebSocketException):
    """
    This error indicates that the connection has been offline for too long without being able to reconnect.
    """

class ActionRequiresAuthentication(BfxWebSocketException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

class InvalidAuthenticationCredentials(BfxWebSocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

class UnknownChannelError(BfxWebSocketException):
    """
    Thrown when a user attempts to subscribe to an unknown channel.
    """

class UnknownEventError(BfxWebSocketException):
    """
    Thrown when a user attempts to add a listener for an unknown event.
    """

class OutdatedClientVersion(BfxWebSocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """
