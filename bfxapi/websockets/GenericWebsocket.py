import asyncio
import websockets
import json

from ..utils.CustomLogger import CustomLogger

class AuthError(Exception): pass

def is_json(myjson):
  try:
      json_object = json.loads(myjson)
  except ValueError as e:
      return False
  return True

class GenericWebsocket(object):
  def __init__(self, host, symbol='tBTCUSD', onCandleHook=None, onTradeHook=None, onCompleteHook=None):
    if not onCandleHook:
      raise KeyError("Expected `onCandleHook` in parameters.")
    if not onTradeHook:
      raise KeyError("Expected `onTradeHook` in parameters.")
    if not onCompleteHook:
      raise KeyError("Expected `onCompleteHook` in parameters.")
    self.onCandleHook = onCandleHook
    self.onTradeHook = onTradeHook
    self.onCompleteHook = onCompleteHook
    self.symbol = symbol
    self.host = host
    self.awaiting_request = False

    self.logger = CustomLogger('HFWebSocket', logLevel='INFO')
    self.loop = asyncio.get_event_loop()
    # self.events = EventEmitter()

  def run(self):
    self.loop.run_until_complete(self._main(self.host))

  async def _main(self, host):
    async with websockets.connect(host) as websocket:
      self.ws = websocket
      while True:
        await asyncio.sleep(0)
        message = await websocket.recv()
        await self.on_message(message)

  async def on_error(self, error):
    self.logger.error(error)

  async def on_close(self):
    self.logger.info("Websocket closed.")
    await self.ws.close()
    self.onCompleteHook()

  async def on_open(self):
    pass

  async def on_message(self, message):
    pass
