from typing import Optional
from .rest_public_endpoints import RestPublicEndpoints
from .rest_authenticated_endpoints import RestAuthenticatedEndpoints

class BfxRestInterface(object):
    VERSION = 2

    def __init__(self, host: str, API_KEY: Optional[str] = None, API_SECRET: Optional[str] = None):
        self.public = RestPublicEndpoints(host=host)

        self.auth = RestAuthenticatedEndpoints(host=host, API_KEY=API_KEY, API_SECRET=API_SECRET)