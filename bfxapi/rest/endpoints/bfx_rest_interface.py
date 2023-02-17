from typing import Optional

from .rest_public_endpoints import RestPublicEndpoints
from .rest_authenticated_endpoints import RestAuthenticatedEndpoints
from .rest_merchant_endpoints import RestMerchantEndpoints

class BfxRestInterface(object):
    VERSION = 2

    def __init__(self, host, credentials = None):
        API_KEY, API_SECRET = credentials and \
            (credentials["API_KEY"], credentials["API_SECRET"]) or (None, None)

        self.public = RestPublicEndpoints(host=host)       
        self.auth = RestAuthenticatedEndpoints(host=host, API_KEY=API_KEY, API_SECRET=API_SECRET)
        self.merchant = RestMerchantEndpoints(host=host, API_KEY=API_KEY, API_SECRET=API_SECRET)