from typing import \
    TYPE_CHECKING, Optional, cast

from bfxapi.websocket.exceptions import \
    ConnectionNotOpen, ActionRequiresAuthentication

if TYPE_CHECKING:
    from websockets.client import WebSocketClientProtocol

class Connection:
    HEARTBEAT = "hb"

    class Authenticable:
        def __init__(self) -> None:
            self._authentication: bool = False

        @property
        def authentication(self) -> bool:
            return self._authentication

        @staticmethod
        def require_websocket_authentication(function):
            async def wrapper(self, *args, **kwargs):
                if not self.authentication:
                    raise ActionRequiresAuthentication("To perform this action you need to " \
                        "authenticate using your API_KEY and API_SECRET.")

                internal = Connection.require_websocket_connection(function)

                return await internal(self, *args, **kwargs)

            return wrapper

    def __init__(self, host: str) -> None:
        self._host = host

        self.__protocol: Optional["WebSocketClientProtocol"] = None

    @property
    def open(self) -> bool:
        return self.__protocol is not None and \
            self.__protocol.open

    @property
    def _websocket(self) -> "WebSocketClientProtocol":
        return cast("WebSocketClientProtocol", self.__protocol)

    @_websocket.setter
    def _websocket(self, protocol: "WebSocketClientProtocol") -> None:
        self.__protocol = protocol

    @staticmethod
    def require_websocket_connection(function):
        async def wrapper(self, *args, **kwargs):
            if self.open:
                return await function(self, *args, **kwargs)

            raise ConnectionNotOpen("No open connection with the server.")

        return wrapper
