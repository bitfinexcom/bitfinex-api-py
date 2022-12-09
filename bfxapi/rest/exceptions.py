__all__ = [
    "RequestParametersError",
    "ResourceNotFound"
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