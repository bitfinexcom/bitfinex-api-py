from typing import List, Literal, Optional

from bfxapi._utils.logger import ColorLogger

from bfxapi.rest import BfxRestInterface
from bfxapi.websocket import BfxWebSocketClient
from bfxapi.urls import REST_HOST, WSS_HOST

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
            log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    ) -> None:
        logger = ColorLogger("bfxapi", level=log_level)

        if log_filename:
            logger.register(filename=log_filename)

        self.rest = BfxRestInterface(rest_host, api_key, api_secret)

        self.wss = BfxWebSocketClient(wss_host, api_key, api_secret,
            filters=filters, wss_timeout=wss_timeout, logger=logger)
