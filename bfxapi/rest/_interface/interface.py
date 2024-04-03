from typing import Optional

from .middleware import Middleware


class Interface:
    def __init__(
        self, host: str, api_key: Optional[str] = None, api_secret: Optional[str] = None
    ):
        self._m = Middleware(host, api_key, api_secret)
