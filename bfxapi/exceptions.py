__all__ = [
    "BfxBaseException",
    
    "LabelerSerializerException",
    "IntegerUnderflowError",
    "IntegerOverflowflowError"
]

class BfxBaseException(Exception):
    """
    Base class for every custom exception in bfxapi/rest/exceptions.py and bfxapi/websocket/exceptions.py.
    """

    pass

class LabelerSerializerException(BfxBaseException):
    """
    This exception indicates an error thrown by the _Serializer class in bfxapi/labeler.py.
    """

    pass

class IntegerUnderflowError(BfxBaseException):
    """
    This error indicates an underflow in one of the integer types defined in bfxapi/utils/integers.py.
    """

    pass

class IntegerOverflowflowError(BfxBaseException):
    """
    This error indicates an overflow in one of the integer types defined in bfxapi/utils/integers.py.
    """

    pass