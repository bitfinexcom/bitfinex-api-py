from .rest import BfxRestInterface
from .websocket import BfxWebsocketClient

from typing import List, Optional

from enum import Enum

class Constants(str, Enum):
    REST_HOST = "https://api.bitfinex.com/v2"
    PUB_REST_HOST = "https://api-pub.bitfinex.com/v2"
    STAGING_REST_HOST = "https://api.staging.bitfinex.com/v2"

    WSS_HOST = "wss://api.bitfinex.com/ws/2"
    PUB_WSS_HOST = "wss://api-pub.bitfinex.com/ws/2"
    STAGING_WSS_HOST = "wss://api.staging.bitfinex.com/ws/2"

class Client(object):
    def __init__(
            self,
            REST_HOST: str = Constants.REST_HOST,
            WSS_HOST: str = Constants.WSS_HOST,
            API_KEY: Optional[str] = None,
            API_SECRET: Optional[str] = None,
            filter: Optional[List[str]] = None,
            log_level: str = "INFO"
    ):
        credentials = { 
            "API_KEY": API_KEY, 
            "API_SECRET": API_SECRET, 
            "filter": filter 
        }

        self.rest = BfxRestInterface(
            host=REST_HOST,
            API_KEY=API_KEY,
            API_SECRET=API_SECRET
        )

        self.wss = BfxWebsocketClient(
            host=WSS_HOST, 
            credentials=credentials, 
            log_level=log_level
        )