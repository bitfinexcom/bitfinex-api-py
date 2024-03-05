import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar, cast

from typing_extensions import Concatenate, ParamSpec
from websockets.client import WebSocketClientProtocol

from bfxapi.websocket.exceptions import ActionRequiresAuthentication, ConnectionNotOpen

_S = TypeVar("_S", bound="Connection")

_R = TypeVar("_R")

_P = ParamSpec("_P")


class Connection(ABC):
    _HEARTBEAT = "hb"

    def __init__(self, host: str) -> None:
        self._host = host

        self._authentication: bool = False

        self.__protocol: Optional[WebSocketClientProtocol] = None

    @property
    def open(self) -> bool:
        return self.__protocol is not None and self.__protocol.open

    @property
    def authentication(self) -> bool:
        return self._authentication

    @property
    def _websocket(self) -> WebSocketClientProtocol:
        return cast(WebSocketClientProtocol, self.__protocol)

    @_websocket.setter
    def _websocket(self, protocol: WebSocketClientProtocol) -> None:
        self.__protocol = protocol

    @abstractmethod
    async def start(self) -> None: ...

    @staticmethod
    def _require_websocket_connection(
        function: Callable[Concatenate[_S, _P], Awaitable[_R]],
    ) -> Callable[Concatenate[_S, _P], Awaitable[_R]]:
        @wraps(function)
        async def wrapper(self: _S, *args: Any, **kwargs: Any) -> _R:
            if self.open:
                return await function(self, *args, **kwargs)

            raise ConnectionNotOpen("No open connection with the server.")

        return wrapper

    @staticmethod
    def _require_websocket_authentication(
        function: Callable[Concatenate[_S, _P], Awaitable[_R]],
    ) -> Callable[Concatenate[_S, _P], Awaitable[_R]]:
        @wraps(function)
        async def wrapper(self: _S, *args: Any, **kwargs: Any) -> _R:
            if not self.authentication:
                raise ActionRequiresAuthentication(
                    "To perform this action you need to "
                    "authenticate using your API_KEY and API_SECRET."
                )

            internal = Connection._require_websocket_connection(function)

            return await internal(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def _get_authentication_message(
        api_key: str, api_secret: str, filters: Optional[List[str]] = None
    ) -> str:
        message: Dict[str, Any] = {
            "event": "auth",
            "filter": filters,
            "apiKey": api_key,
        }

        message["authNonce"] = round(datetime.now().timestamp() * 1_000_000)

        message["authPayload"] = f"AUTH{message['authNonce']}"

        auth_sig = hmac.new(
            key=api_secret.encode("utf8"),
            msg=message["authPayload"].encode("utf8"),
            digestmod=hashlib.sha384,
        )

        message["authSig"] = auth_sig.hexdigest()

        return json.dumps(message)
