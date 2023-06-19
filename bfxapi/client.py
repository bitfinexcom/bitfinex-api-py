from typing import List, Literal, Optional

from .rest import BfxRestInterface
from .websocket import BfxWebSocketClient
from .urls import REST_HOST, WSS_HOST

class Client:
    def __init__(
            self,
            api_key: Optional[str] = None,
            api_secret: Optional[str] = None,
            *,
            rest_host: str = REST_HOST,
            wss_host: str = WSS_HOST,
            filters: Optional[List[str]] = None,
            wss_timeout: Optional[float] = 60 * 15,
            log_filename: Optional[str] = None,
            log_level: Literal["ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    ) -> None:
        self.rest = BfxRestInterface(rest_host, api_key, api_secret)

        self.wss = BfxWebSocketClient(wss_host, api_key, api_secret,
            filters=filters, wss_timeout=wss_timeout, log_filename=log_filename,
                log_level=log_level)
