import json, asyncio, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .manager import Manager

from .channels import Channels

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

                    if isinstance(message, list):
                        chanId, parameters = message[0], message[1:]
                        subscription = self.chanIds[chanId]
                        self.manager.handle(subscription, *parameters)
            except websockets.ConnectionClosed:
                continue
        
    async def subscribe(self, channel, **kwargs):
        if self.websocket == None:
            return self.channels.append((channel, kwargs))

        await self.websocket.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            **kwargs
        }))

    def on(self, event):
        def handler(function):
            self.event_emitter.on(event, function)

        return handler 