from typing import Optional

from bfxapi.rest._interfaces import (
    RestAuthEndpoints,
    RestMerchantEndpoints,
    RestPublicEndpoints,
)


class BfxRestInterface:
    def __init__(
        self, host: str, api_key: Optional[str] = None, api_secret: Optional[str] = None
    ):
        self.auth = RestAuthEndpoints(host=host, api_key=api_key, api_secret=api_secret)

        self.merchant = RestMerchantEndpoints(
            host=host, api_key=api_key, api_secret=api_secret
        )

        self.public = RestPublicEndpoints(host=host)
