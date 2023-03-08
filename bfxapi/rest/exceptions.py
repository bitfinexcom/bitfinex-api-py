from .. exceptions import BfxBaseException

__all__ = [
    "BfxRestException",

    "ResourceNotFound",
    "RequestParametersError",
    "ResourceNotFound",
    "InvalidAuthenticationCredentials"
]

class BfxRestException(BfxBaseException):
    """
    Base class for all custom exceptions in bfxapi/rest/exceptions.py.
    """

class ResourceNotFound(BfxRestException):
    """
    This error indicates a failed HTTP request to a non-existent resource.
    """

class RequestParametersError(BfxRestException):
    """
    This error indicates that there are some invalid parameters sent along with an HTTP request.
    """

class InvalidAuthenticationCredentials(BfxRestException):
    """
    This error indicates that the user has provided incorrect credentials (API-KEY and API-SECRET) for authentication.
    """

class UnknownGenericError(BfxRestException):
    """
    This error indicates an undefined problem processing an HTTP request sent to the APIs.
    """
