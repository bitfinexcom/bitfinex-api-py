__all__ = [
    "RequestParametersError"
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