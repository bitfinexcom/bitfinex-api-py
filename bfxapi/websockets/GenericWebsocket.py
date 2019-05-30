"""
Module used as a interfeace to describe a generick websocket client
"""

import asyncio
import websockets
import socket
import json

from pyee import EventEmitter
from ..utils.CustomLogger import CustomLogger

# websocket exceptions
from websockets.exceptions import ConnectionClosed

class AuthError(Exception):
    """
    Thrown whenever there is a problem with the authentication packet
    """
    pass

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

class GenericWebsocket:
    """
    Websocket object used to contain the base functionality of a websocket.
    Inlcudes an event emitter and a standard websocket client.
    """

    def __init__(self, host, logLevel='INFO', loop=None, max_retries=5):
        self.host = host
        self.logger = CustomLogger('BfxWebsocket', logLevel=logLevel)
        self.loop = loop or asyncio.get_event_loop()
        self.events = EventEmitter(
            scheduler=asyncio.ensure_future, loop=self.loop)
        # overide 'error' event to stop it raising an exception
        # self.events.on('error', self.on_error)
        self.ws = None
        self.max_retries = max_retries
        self.attempt_retry = True

    def run(self):
        """
        Run the websocket connection indefinitely
        """
        if self.loop.is_running():
            asyncio.ensure_future(self._main(self.host))
        else:
            self.loop.run_until_complete(self._main(self.host))

    def get_task_executable(self):
        """
        Get the run indefinitely asyncio task
        """
        return self._main(self.host)

    async def _connect(self, host):
        async with websockets.connect(host) as websocket:
            self.ws = websocket
            self.logger.info("Wesocket connected to {}".format(host))
            while True:
                await asyncio.sleep(0)
                message = await websocket.recv()
                await self.on_message(message)

    def get_ws(self):
        return self.ws

    async def _main(self, host):
        retries = 0
        while retries < self.max_retries and self.attempt_retry:
            try:
                await self._connect(host)
                retries = 0
            except (Exception) as e:
                self._emit('disconnected')
                if (not self.attempt_retry):
                    return
                self.logger.error(str(e))
                retries += 1
                # wait 5 seconds befor retrying
                self.logger.info("Waiting 5 seconds before retrying...")
                await asyncio.sleep(5)
                self.logger.info("Reconnect attempt {}/{}".format(retries, self.max_retries))
        self.logger.info("Unable to connect to websocket.")
        self._emit('stopped')

    def remove_all_listeners(self, event):
        """
        Remove all listeners from event emitter
        """
        self.events.remove_all_listeners(event)

    def on(self, event, func=None):
        """
        Add a new event to the event emitter
        """
        if not func:
            return self.events.on(event)
        self.events.on(event, func)

    def once(self, event, func=None):
        """
        Add a new event to only fire once to the event
        emitter
        """
        if not func:
            return self.events.once(event)
        self.events.once(event, func)

    def _emit(self, event, *args, **kwargs):
        self.events.emit(event, *args, **kwargs)

    async def on_error(self, error):
        """
        On websocket error print and fire event
        """
        self.logger.error(error)

    async def on_close(self):
        """
        On websocket close print and fire event. This is used by the data server.
        """
        self.logger.info("Websocket closed.")
        self.attempt_retry = False
        await self.ws.close()
        self._emit('done')

    async def on_open(self):
        """
        On websocket open
        """
        pass

    async def on_message(self, message):
        """
        On websocket message
        """
        pass
