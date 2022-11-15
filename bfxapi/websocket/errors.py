__all__ = [
    "BfxWebsocketException",
    "ConnectionNotOpen",
    "InvalidAuthenticationCredentials"
]

class BfxWebsocketException(Exception):
    """
    Base class for all exceptions defined in bfx/websocket/errors.py.
    """

    pass

class ConnectionNotOpen(BfxWebsocketException):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

    pass

class InvalidAuthenticationCredentials(BfxWebsocketException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

    pass

class OutdatedClientVersion(BfxWebsocketException):
    """
    This error indicates a mismatch between the client version and the server WSS version.
    """

    pass