from .rest_public_endpoints import RestPublicEndpoints
from .rest_auth_endpoints import RestAuthEndpoints
from .rest_merchant_endpoints import RestMerchantEndpoints

class BfxRestInterface:
    VERSION = 2

    def __init__(self, host, api_key = None, api_secret = None):
        self.public = RestPublicEndpoints(host=host)
        self.auth = RestAuthEndpoints(host=host, api_key=api_key, api_secret=api_secret)
        self.merchant = RestMerchantEndpoints(host=host, api_key=api_key, api_secret=api_secret)
