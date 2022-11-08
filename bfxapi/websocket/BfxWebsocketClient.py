import json, asyncio, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .manager import Manager
from .channels import Channels
from .errors import ConnectionNotOpen

class BfxWebsocketClient(object):
    def __init__(self, host, channels=None):
        self.host, self.chanIds, self.event_emitter = host, dict(), AsyncIOEventEmitter()

        self.manager, self.websocket = Manager(event_emitter=self.event_emitter), None

        self.channels = channels or list()

    def run_forever(self):
        asyncio.run(self.connect())

    async def connect(self):
        async for websocket in websockets.connect(self.host):
            try:
                self.websocket = websocket

                for channel, parameters in self.channels:
                    await self.subscribe(channel, **parameters)
                else: self.event_emitter.emit("open")

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "subscribed":
                        del message["event"]
                        self.chanIds[message["chanId"]] = message
                        self.event_emitter.emit("subscribed", message)

                    elif isinstance(message, dict) and message["event"] == "unsubscribed":
                        if message["status"] == "OK":
                            del self.chanIds[message["chanId"]]

                    elif isinstance(message, list):
                        chanId, parameters = message[0], message[1:]
                        self.manager.handle(self.chanIds[chanId], *parameters)
            except websockets.ConnectionClosed:
                continue
        
    def __require_websocket_connection(function):
        async def wrapper(self, *args, **kwargs):
            if self.websocket == None or self.websocket.open == False:
                raise ConnectionNotOpen("No open connection with the server.")
        
            await function(self, *args, **kwargs)

        return wrapper

    @__require_websocket_connection
    async def subscribe(self, channel, **kwargs):
        await self.websocket.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            **kwargs
        }))

    @__require_websocket_connection
    async def unsubscribe(self, chanId):
        await self.websocket.send(json.dumps({
            "event": "unsubscribe",
            "chanId": chanId
        }))

    async def clear(self):
        for chanId in self.chanIds.keys():
            await self.unsubscribe(chanId)

    def on(self, event):
        def handler(function):
            self.event_emitter.on(event, function)

        return handler 