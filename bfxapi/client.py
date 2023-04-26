from typing import List, Literal, Optional

from .rest import BfxRestInterface
from .websocket import BfxWebSocketClient
from .urls import REST_HOST, WSS_HOST

class Client:
    def __init__(
            self,
            api_key: Optional[str] = None,
            api_secret: Optional[str] = None,
            filters: Optional[List[str]] = None,
            *,
            rest_host: str = REST_HOST,
            wss_host: str = WSS_HOST,
            wss_timeout: Optional[float] = 60 * 15,
            log_filename: Optional[str] = None,
            log_level: Literal["ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    ):
        credentials = None

        if api_key and api_secret:
            credentials = { "api_key": api_key, "api_secret": api_secret, "filters": filters }

        self.rest = BfxRestInterface(
            host=rest_host,
            credentials=credentials
        )

        self.wss = BfxWebSocketClient(
            host=wss_host,
            credentials=credentials,
            wss_timeout=wss_timeout,
            log_filename=log_filename,
            log_level=log_level
        )
        