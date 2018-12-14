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

  def __init__(self, host, logLevel='INFO', loop=None):
    self.host = host
    self.logger = CustomLogger('BfxWebsocket', logLevel=logLevel)
    self.loop = loop or asyncio.get_event_loop()
    self.events = EventEmitter(scheduler=asyncio.ensure_future, loop=self.loop)
    self.ws = None

  def run(self):
    self.loop.run_until_complete(self._main(self.host))

  def get_task_executable(self):
    return self._main(self.host)

  async def _main(self, host):
    async with websockets.connect(host) as websocket:
      self.ws = websocket
      self.logger.info("Wesocket connectedt to {}".format(self.host))
      while True:
        await asyncio.sleep(0)
        message = await websocket.recv()
        await self.on_message(message)

  def remove_all_listeners(self, event):
    self.events.remove_all_listeners(event)

  def on(self, event, func=None):
    if not func:
      return self.events.on(event)
    self.events.on(event, func)

  def once(self, event, func=None):
    if not func:
      return self.events.once(event)
    self.events.once(event, func)

  def _emit(self, event, *args, **kwargs):
    self.events.emit(event, *args, **kwargs)

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
