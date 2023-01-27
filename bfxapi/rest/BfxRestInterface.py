from typing import Optional

from ._RestPublicEndpoints import _RestPublicEndpoints

from ._RestAuthenticatedEndpoints import _RestAuthenticatedEndpoints

class BfxRestInterface(object):
    VERSION = 2

    def __init__(self, host: str, API_KEY: Optional[str] = None, API_SECRET: Optional[str] = None):
        self.public = _RestPublicEndpoints(host=host)

        self.auth = _RestAuthenticatedEndpoints(host=host, API_KEY=API_KEY, API_SECRET=API_SECRET)