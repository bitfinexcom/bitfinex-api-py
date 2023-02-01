import time, hmac, hashlib, json, requests

from http import HTTPStatus
from .enums import Error
from .exceptions import ResourceNotFound, RequestParametersError, InvalidAuthenticationCredentials, UnknownGenericError

from ..utils.JSONEncoder import JSONEncoder

class _Requests(object):
    def __init__(self, host, API_KEY = None, API_SECRET = None):
        self.host, self.API_KEY, self.API_SECRET = host, API_KEY, API_SECRET

    def __build_authentication_headers(self, endpoint, data):
        nonce = str(int(time.time()) * 1000)

        path = f"/api/v2/{endpoint}{nonce}"

        if data != None: path += data

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

    def _GET(self, endpoint, params = None):
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

    def _POST(self, endpoint, params = None, data = None, _ignore_authentication_headers = False):
        headers = { "Content-Type": "application/json" }

        if isinstance(data, dict):
            data = json.dumps({ key: value for key, value in data.items() if value != None}, cls=JSONEncoder)

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