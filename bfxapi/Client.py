from .websockets.BfxWebsocket import BfxWebsocket

class Client:
  def __init__(self, API_KEY=None, API_SECRET=None,
      host='wss://test.bitfinex.com/ws/2', *args, **kwargs):
    self.ws = BfxWebsocket(API_KEY=API_KEY, API_SECRET=API_SECRET, host=host, *args, **kwargs)
    self.rest = None # Eventually will be the rest interface
