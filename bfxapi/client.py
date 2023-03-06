from typing import List, Optional

from .rest import BfxRestInterface
from .websocket import BfxWebsocketClient
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
            log_filename: Optional[str] = None,
            log_level: str = "INFO"
    ):
        credentials = None

        if api_key and api_secret:
            credentials = { "api_key": api_key, "api_secret": api_secret, "filters": filters }

        self.rest = BfxRestInterface(
            host=rest_host,
            credentials=credentials
        )

        self.wss = BfxWebsocketClient(
            host=wss_host,
            credentials=credentials,
            log_filename=log_filename,
            log_level=log_level
        )
        