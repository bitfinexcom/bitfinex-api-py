# pylint: disable-next=wildcard-import,unused-wildcard-import
from bfxapi._exceptions import *

class ResourceNotFound(BfxBaseException):
    """
    This error indicates a failed HTTP request to a non-existent resource.
    """

class RequestParametersError(BfxBaseException):
    """
    This error indicates that there are some invalid parameters sent along with an HTTP request.
    """

class UnknownGenericError(BfxBaseException):
    """
    This error indicates an undefined problem processing an HTTP request sent to the APIs.
    """
