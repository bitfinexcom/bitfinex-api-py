from typing import \
    TYPE_CHECKING, Optional, cast

from bfxapi.websocket.exceptions import \
    ConnectionNotOpen

if TYPE_CHECKING:
    from websockets.client import WebSocketClientProtocol

class Connection:
    HEARTBEAT = "hb"

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
