from bfxapi.exceptions import BfxBaseException

class NotFoundError(BfxBaseException):
    pass

class RequestParametersError(BfxBaseException):
    pass

class UnknownGenericError(BfxBaseException):
    pass
