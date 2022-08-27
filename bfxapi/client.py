"""
This module exposes the core bitfinex clients which includes both
a websocket client and a rest interface client
"""

# pylint: disable-all

from .websockets.bfx_websocket import BfxWebsocket
from .rest.bfx_rest import BfxRest
from .constants import *

class Client:
    """
    The bfx client exposes rest and websocket objects
    """

    def __init__(self, API_KEY=None, API_SECRET=None, rest_host=REST_HOST,
                 ws_host=WS_HOST, create_event_emitter=None, logLevel='INFO', dead_man_switch=False,
                 ws_capacity=25, channel_filter=[], *args, **kwargs):
        self.ws = BfxWebsocket(API_KEY=API_KEY, API_SECRET=API_SECRET, host=ws_host,
                               logLevel=logLevel, dead_man_switch=dead_man_switch, channel_filter=channel_filter,
                               ws_capacity=ws_capacity, create_event_emitter=create_event_emitter, *args, **kwargs)
        self.rest = BfxRest(API_KEY=API_KEY, API_SECRET=API_SECRET, host=rest_host,
                            logLevel=logLevel, *args, **kwargs)
