from typing import TYPE_CHECKING, Any, Optional

from .middleware import Middleware

if TYPE_CHECKING:
    from requests.sessions import _Params


class Interface:
    def __init__(
        self, host: str, api_key: Optional[str] = None, api_secret: Optional[str] = None
    ):
        self.__middleware = Middleware(host, api_key, api_secret)

    def _get(self, endpoint: str, params: Optional["_Params"] = None) -> Any:
        return self.__middleware.get(endpoint, params)

    def _post(
        self,
        endpoint: str,
        body: Optional[Any] = None,
        params: Optional["_Params"] = None,
    ) -> Any:
        return self.__middleware.post(endpoint, body, params)
