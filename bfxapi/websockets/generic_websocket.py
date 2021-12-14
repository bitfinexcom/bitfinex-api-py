"""
Module used as a interfeace to describe a generick websocket client
"""

import asyncio
import websockets
import socket
import json
import time
from threading import Thread, Lock

from pyee import AsyncIOEventEmitter
from ..utils.custom_logger import CustomLogger

# websocket exceptions
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

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

class Socket():
    def __init__(self, sId):
        self.ws = None
        self.isConnected = False
        self.isAuthenticated = False
        self.id = sId
        self.lock = Lock()

    def set_connected(self):
        self.isConnected = True

    def set_disconnected(self):
        self.isConnected = False

    def set_authenticated(self):
        self.isAuthenticated = True

    def set_unauthenticated(self):
        self.isAuthenticated = False

    def set_websocket(self, ws):
        self.ws = ws

    async def send(self, data):
        with self.lock:
            await self.ws.send(data)

def _start_event_worker():
    return AsyncIOEventEmitter()

class GenericWebsocket:
    """
    Websocket object used to contain the base functionality of a websocket.
    Inlcudes an event emitter and a standard websocket client.
    """
    logger = CustomLogger('BfxWebsocket', logLevel="DEBUG")

    def __init__(self, host, logLevel='INFO', max_retries=5, create_event_emitter=None):
        self.host = host
        self.logger.set_level(logLevel)
        # overide 'error' event to stop it raising an exception
        # self.events.on('error', self.on_error)
        self.ws = None
        self.max_retries = max_retries
        self.attempt_retry = True
        self.sockets = {}
        # start separate process for the even emitter
        create_ee = create_event_emitter or _start_event_worker
        self.events = create_ee()

    def run(self):
        """
        Start the websocket connection. This functions spawns the initial socket
        thread and connection.
        """
        self._start_new_socket()
        event_loop = asyncio.get_event_loop()
        if not event_loop or not event_loop.is_running():
            while True:
                time.sleep(1)

    def get_task_executable(self):
        """
        Get the run indefinitely asyncio task
        """
        return self._run_socket()

    def _start_new_async_socket(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._run_socket())

    def _start_new_socket(self, socketId=None):
        if not socketId:
            socketId = len(self.sockets)
        worker = Thread(target=self._start_new_async_socket)
        worker.start()
        return socketId

    def _wait_for_socket(self, socket_id):
        """
        Block until the given socket connection is open
        """
        while True:
            socket = self.sockets.get(socket_id, False)
            if socket:
                if socket.isConnected and socket.ws:
                    return
            time.sleep(0.01)

    def get_socket(self, socketId):
        return self.sockets[socketId]

    def get_authenticated_socket(self):
        for socketId in self.sockets:
            if self.sockets[socketId].isAuthenticated:
                return self.sockets[socketId]
        return None

    async def _run_socket(self):
        retries = 0
        sId =  len(self.sockets)
        s = Socket(sId)
        self.sockets[sId] = s
        loop = asyncio.get_event_loop()
        while self.max_retries == 0 or (retries < self.max_retries and self.attempt_retry):
            try:
                async with websockets.connect(self.host) as websocket:
                    self.sockets[sId].set_websocket(websocket)
                    self.sockets[sId].set_connected()
                    self.logger.info("Websocket connected to {}".format(self.host))
                    retries = 0
                    while True:
                        # optimization - wait 0 seconds to force the async queue
                        # to be cleared before continuing
                        await asyncio.sleep(0)
                        message = await websocket.recv()
                        await self.on_message(sId, message)
            except (ConnectionClosed, socket.error, InvalidStatusCode) as e:
                self.sockets[sId].set_disconnected()
                if self.sockets[sId].isAuthenticated:
                    self.sockets[sId].set_unauthenticated()
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

    async def stop(self):
        """
        Stop all websocket connections
        """
        self.attempt_retry = False
        for key, socket in self.sockets.items():
            await socket.ws.close()
        self._emit('done')

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
        if type(event) == Exception:
            self.logger.error(event)
        self.events.emit(event, *args, **kwargs)

    async def on_error(self, error):
        """
        On websocket error print and fire event
        """
        self.logger.error(error)

    async def on_close(self):
        """
        This is used by the HF data server.
        """
        self.stop()

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
