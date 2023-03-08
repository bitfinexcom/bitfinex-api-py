__all__ = [
    "BfxBaseException",

    "LabelerSerializerException",
]

class BfxBaseException(Exception):
    """
    Base class for every custom exception in bfxapi/rest/exceptions.py and bfxapi/websocket/exceptions.py.
    """

class LabelerSerializerException(BfxBaseException):
    """
    This exception indicates an error thrown by the _Serializer class in bfxapi/labeler.py.
    """
    