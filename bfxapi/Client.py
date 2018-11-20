import asyncio

from .websockets.BfxWebsocket import BfxWebsocket
from .rest.BfxRest import BfxRest

class Client:
  def __init__(self, API_KEY=None, API_SECRET=None, rest_host='https://api.bitfinex.com/v2',
      ws_host='wss://api.bitfinex.com/ws/2', loop=None, logLevel='INFO', *args, **kwargs):
    self.loop = loop or asyncio.get_event_loop()
    self.ws = BfxWebsocket(API_KEY=API_KEY, API_SECRET=API_SECRET, host=ws_host,
        loop=self.loop, *args, **kwargs)
    self.rest = BfxRest(API_KEY=API_KEY, API_SECRET=API_SECRET, host=rest_host,
        loop=self.loop, *args, **kwargs)
