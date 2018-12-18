"""
This module exposes the core bitfinex clients which includes both
a websocket client and a rest interface client
"""

# pylint: disable-all

import asyncio

from .websockets.BfxWebsocket import BfxWebsocket
from .rest.BfxRest import BfxRest

REST_HOST = 'https://api.bitfinex.com/v2'
WS_HOST = 'wss://api.bitfinex.com/ws/2'

class Client:
    """
    The bfx client exposes rest and websocket objects
    """

    def __init__(self, API_KEY=None, API_SECRET=None, rest_host=REST_HOST,
                 ws_host=WS_HOST, loop=None, logLevel='INFO', dead_man_switch=False,
                 *args, **kwargs):
        self.loop = loop or asyncio.get_event_loop()
        self.ws = BfxWebsocket(API_KEY=API_KEY, API_SECRET=API_SECRET, host=ws_host,
                               loop=self.loop, logLevel=logLevel, dead_man_switch=dead_man_switch,
                               *args, **kwargs)
        self.rest = BfxRest(API_KEY=API_KEY, API_SECRET=API_SECRET, host=rest_host,
                            loop=self.loop, logLevel=logLevel, *args, **kwargs)
