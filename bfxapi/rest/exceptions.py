__all__ = [
    "RequestParametersError",
    "ResourceNotFound",
    "InvalidAuthenticationCredentials"
]

class BfxRestException(Exception):
    """
    Base class for all exceptions defined in bfxapi/rest/exceptions.py.
    """

    pass

class RequestParametersError(BfxRestException):
    """
    This error indicates that there are some invalid parameters sent along with an HTTP request.
    """

    pass

class ResourceNotFound(BfxRestException):
    """
    This error indicates a failed HTTP request to a non-existent resource.
    """

    pass

class InvalidAuthenticationCredentials(BfxRestException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

    pass