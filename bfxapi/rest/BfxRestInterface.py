import requests
from . import serializers
from .typings import PlatformStatus

class BfxRestInterface(object):
    def __init__(self, host):
        self.host = host

    def platform_status(self) -> PlatformStatus:
        return serializers.PlatformStatus.parse(
            *requests.get(f"{self.host}/platform/status").json()
        )
