import json, asyncio, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .channels import Channels

class BfxWebsocketClient(object):
    def __init__(self, host, channels=None):
        self.host = host

        self.chanIds, self.event_emitter = dict(), AsyncIOEventEmitter()

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
                        self.chanIds[message["chanId"]] = message

                        self.event_emitter.emit("subscribed", message)

                    if isinstance(message, list):
                        chanId, parameters = message[0], message[1:]

                        subscription = self.chanIds[chanId]

                        if subscription["channel"] == Channels.TICKER:
                            self.event_emitter.emit("ticker", subscription, parameters[0])

                        if subscription["channel"] == Channels.TRADES:
                            if len(parameters) == 1:
                                self.event_emitter.emit("trades_snapshot", subscription, parameters[0])

                            if len(parameters) == 2:
                                self.event_emitter.emit("trades_update", subscription, parameters[0], parameters[1])

                        if subscription["channel"] == Channels.BOOK:
                            if all(isinstance(element, list) for element in parameters[0]):
                                self.event_emitter.emit("book_snapshot", subscription, parameters[0])
                            else: self.event_emitter.emit("book_update", subscription, parameters[0])
            except websockets.ConnectionClosed:
                continue
        
    async def subscribe(self, channel, **kwargs):
        await self.websocket.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            **kwargs
        }))

    def on(self, event):
        def handler(function):
            self.event_emitter.on(event, function)

        return handler 
