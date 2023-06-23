from .rest_public_endpoints import RestPublicEndpoints
from .rest_authenticated_endpoints import RestAuthenticatedEndpoints
from .rest_merchant_endpoints import RestMerchantEndpoints

class BfxRestInterface:
    VERSION = 2

    def __init__(self, host, credentials = None):
        api_key, api_secret = (credentials['api_key'], credentials['api_secret']) if credentials else (None, None)

        self.public = RestPublicEndpoints(host=host)
        self.auth = RestAuthenticatedEndpoints(host=host, api_key=api_key, api_secret=api_secret)
        self.merchant = RestMerchantEndpoints(host=host, api_key=api_key, api_secret=api_secret)
