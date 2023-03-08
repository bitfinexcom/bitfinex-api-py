from typing import TYPE_CHECKING, Optional, Any

from http import HTTPStatus

import time, hmac, hashlib, json, requests

from ..enums import Error
from ..exceptions import ResourceNotFound, RequestParametersError, InvalidAuthenticationCredentials, UnknownGenericError
from ...utils.json_encoder import JSONEncoder

if TYPE_CHECKING:
    from requests.sessions import _Params

class Middleware:
    TIMEOUT = 30

    def __init__(self, host: str, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.host, self.api_key, self.api_secret = host, api_key, api_secret

    def __build_authentication_headers(self, endpoint: str, data: Optional[str] = None):
        assert isinstance(self.api_key, str) and isinstance(self.api_secret, str), \
            "API_KEY and API_SECRET must be both str to call __build_authentication_headers"

        nonce = str(round(time.time() * 1_000_000))

        if data is None:
            path = f"/api/v2/{endpoint}{nonce}"
        else: path = f"/api/v2/{endpoint}{nonce}{data}"

        signature = hmac.new(
            self.api_secret.encode("utf8"),
            path.encode("utf8"),
            hashlib.sha384
        ).hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-signature": signature,
            "bfx-apikey": self.api_key
        }

    def _get(self, endpoint: str, params: Optional["_Params"] = None) -> Any:
        response = requests.get(
            url=f"{self.host}/{endpoint}",
            params=params,
            timeout=Middleware.TIMEOUT
        )

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError("The request was rejected with the " \
                    f"following parameter error: <{data[2]}>")

            if data[1] is None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError("The server replied to the request with " \
                    f"a generic error with message: <{data[2]}>.")

        return data

    def _post(self, endpoint: str, params: Optional["_Params"] = None,
            body: Optional[Any] = None, _ignore_authentication_headers: bool = False) -> Any:
        data = body and json.dumps(body, cls=JSONEncoder) or None

        headers = { "Content-Type": "application/json" }

        if self.api_key and self.api_secret and not _ignore_authentication_headers:
            headers = { **headers, **self.__build_authentication_headers(endpoint, data) }

        response = requests.post(
            url=f"{self.host}/{endpoint}",
            params=params,
            data=data,
            headers=headers,
            timeout=Middleware.TIMEOUT
        )

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(f"No resources found at endpoint <{endpoint}>.")

        data = response.json()

        if isinstance(data, list) and len(data) and data[0] == "error":
            if data[1] == Error.ERR_PARAMS:
                raise RequestParametersError("The request was rejected with the " \
                    f"following parameter error: <{data[2]}>")

            if data[1] == Error.ERR_AUTH_FAIL:
                raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")

            if data[1] is None or data[1] == Error.ERR_UNK or data[1] == Error.ERR_GENERIC:
                raise UnknownGenericError("The server replied to the request with " \
                    f"a generic error with message: <{data[2]}>.")

        return data
