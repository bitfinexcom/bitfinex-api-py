import time, hmac, hashlib, json, requests

from typing import TYPE_CHECKING, Optional, Any

from http import HTTPStatus
from ..enums import Error
from ..exceptions import ResourceNotFound, RequestParametersError, InvalidAuthenticationCredentials, UnknownGenericError

from ...utils.JSONEncoder import JSONEncoder

if TYPE_CHECKING:
    from requests.sessions import _Params

class Middleware(object):
    def __init__(self, host: str, API_KEY: Optional[str] = None, API_SECRET: Optional[str] = None):
        self.host, self.API_KEY, self.API_SECRET = host, API_KEY, API_SECRET

    def __build_authentication_headers(self, endpoint: str, data: str):
        assert isinstance(self.API_KEY, str) and isinstance(self.API_SECRET, str), \
            "API_KEY and API_SECRET must be both str to call __build_authentication_headers"

        nonce = str(int(time.time()) * 1000)

        if data == None:
            path = f"/api/v2/{endpoint}{nonce}"
        else: path = f"/api/v2/{endpoint}{nonce}{data}"

        signature = hmac.new(
            self.API_SECRET.encode("utf8"),
            path.encode("utf8"),
            hashlib.sha384 
        ).hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-signature": signature,
            "bfx-apikey": self.API_KEY
        }

    def _GET(self, endpoint: str, params: Optional["_Params"] = None) -> Any:
        response = requests.get(f"{self.host}/{endpoint}", params=params)
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

            if data[1] == None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError(f"The server replied to the request with a generic error with message: <{data[2]}>.")

        return data

    def _POST(self, endpoint: str, params: Optional["_Params"] = None, body: Optional[Any] = None, _ignore_authentication_headers: bool = False) -> Any:
        data = body and json.dumps(body, cls=JSONEncoder) or None

        headers = { "Content-Type": "application/json" }

        if self.API_KEY and self.API_SECRET and _ignore_authentication_headers == False:
            headers = { **headers, **self.__build_authentication_headers(endpoint, data) }

        response = requests.post(f"{self.host}/{endpoint}", params=params, data=data, headers=headers)
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError(f"The request was rejected with the following parameter error: <{data[2]}>")

            if data[1] == Error.ERR_AUTH_FAIL:
                raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")

            if data[1] == None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError(f"The server replied to the request with a generic error with message: <{data[2]}>.")

        return data