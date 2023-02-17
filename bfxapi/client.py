from .rest import BfxRestInterface
from .websocket import BfxWebsocketClient
from .urls import REST_HOST, WSS_HOST

from typing import List, Optional

class Client(object):
    def __init__(
            self,
            REST_HOST: str = REST_HOST,
            WSS_HOST: str = WSS_HOST,
            API_KEY: Optional[str] = None,
            API_SECRET: Optional[str] = None,
            filter: Optional[List[str]] = None,
            log_level: str = "INFO"
    ):
        credentials = None

        if API_KEY and API_SECRET:
            credentials = { "API_KEY": API_KEY, "API_SECRET": API_SECRET, "filter": filter }

        self.rest = BfxRestInterface(
            host=REST_HOST,
            credentials=credentials
        )

        self.wss = BfxWebsocketClient(
            host=WSS_HOST, 
            credentials=credentials, 
            log_level=log_level
        )