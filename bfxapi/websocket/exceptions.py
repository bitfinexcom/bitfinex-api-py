# pylint: disable-next=wildcard-import,unused-wildcard-import
from bfxapi._exceptions import *

class ConnectionNotOpen(BfxBaseException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

class FullBucketError(BfxBaseException):
    """
    Thrown when a user attempts a subscription but all buckets are full.
    """

class ReconnectionTimeoutError(BfxBaseException):
    """
    This error indicates that the connection has been offline for too long without being able to reconnect.
    """

class ActionRequiresAuthentication(BfxBaseException):
    """
    This error indicates an attempt to access a protected resource without logging in first.
    """

class UnknownChannelError(BfxBaseException):
    """
    Thrown when a user attempts to subscribe to an unknown channel.
    """

class UnknownSubscriptionError(BfxBaseException):
    """
    Thrown when a user attempts to reference an unknown subscription.
    """

class UnknownEventError(BfxBaseException):
    """
    Thrown when a user attempts to add a listener for an unknown event.
    """

class VersionMismatchError(BfxBaseException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """
