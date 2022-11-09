class ConnectionNotOpen(Exception):
    """
    This error indicates an attempt to communicate via websocket before starting the connection with the servers.
    """

    pass

class AuthenticationCredentialsError(Exception):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

    pass