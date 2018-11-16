import asyncio
import websockets
import json

from pyee import EventEmitter
from ..utils.CustomLogger import CustomLogger

class AuthError(Exception): pass

def is_json(myjson):
  try:
      json_object = json.loads(myjson)
  except ValueError as e:
      return False
  return True

class GenericWebsocket(object):

  def __init__(self, host, symbol='tBTCUSD', onCandleHook=None, onTradeHook=None, 
      logLevel='ERROR'):
    self.symbol = symbol
    self.host = host
    self.awaiting_request = False
    self.onCandleHook = onCandleHook
    self.onTradeHook = onTradeHook
    self.logger = CustomLogger('HFWebSocket', logLevel=logLevel)
    self.loop = asyncio.get_event_loop()
    self.events = EventEmitter(scheduler=asyncio.ensure_future, loop=self.loop)

  def run(self):
    self.loop.run_until_complete(self._main(self.host))

  async def _main(self, host):
    async with websockets.connect(host) as websocket:
      self.ws = websocket
      while True:
        await asyncio.sleep(0)
        message = await websocket.recv()
        await self.on_message(message)

  def on(self, event, func=None):
    if not func:
      return self.events.on(event)
    self.events.on(event, func)

  def _emit(self, event, *args, **kwargs):
    self.events.emit(event, *args, **kwargs)

  def once(self, event, func):
    self.events.once(event, func)

  async def on_error(self, error):
    self.logger.error(error)
    self.events.emit('error', error)

  async def on_close(self):
    self.logger.info("Websocket closed.")
    await self.ws.close()
    self._emit('done')

  async def on_open(self):
    pass

  async def on_message(self, message):
    pass
