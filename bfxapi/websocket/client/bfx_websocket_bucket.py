from typing import Literal, TypeVar, Callable, cast

import asyncio, json, uuid, websockets

from ..handlers import PublicChannelsHandler

from ..exceptions import ConnectionNotOpen, TooManySubscriptions

_HEARTBEAT = "hb"

F = TypeVar("F", bound=Callable[..., Literal[None]])

def _require_websocket_connection(function: F) -> F:
    async def wrapper(self, *args, **kwargs):
        if self.websocket is None or not self.websocket.open:
            raise ConnectionNotOpen("No open connection with the server.")

        await function(self, *args, **kwargs)

    return cast(F, wrapper)

class BfxWebsocketBucket:
    VERSION = 2

    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter):
        self.host, self.event_emitter, self.on_open_event = host, event_emitter, asyncio.locks.Event()

        self.websocket, self.subscriptions, self.pendings = None, {}, []

        self.handler = PublicChannelsHandler(event_emitter=self.event_emitter)

    async def connect(self):
        reconnection = False

        async for websocket in websockets.connect(self.host):
            self.websocket = websocket

            self.on_open_event.set()

            if reconnection or (reconnection := False):
                for pending in self.pendings:
                    await self.websocket.send(json.dumps(pending))

                for _, subscription in self.subscriptions.items():
                    await self.subscribe(**subscription)

                self.subscriptions.clear()

            try:
                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict):
                        if message["event"] == "subscribed" and (chan_id := message["chanId"]):
                            self.pendings = \
                                [ pending for pending in self.pendings if pending["subId"] != message["subId"] ]

                            self.subscriptions[chan_id] = message

                            self.event_emitter.emit("subscribed", message)
                        elif message["event"] == "unsubscribed" and (chan_id := message["chanId"]):
                            if message["status"] == "OK":
                                del self.subscriptions[chan_id]
                        elif message["event"] == "error":
                            self.event_emitter.emit("wss-error", message["code"], message["msg"])

                    if isinstance(message, list):
                        if (chan_id := message[0]) and message[1] != _HEARTBEAT:
                            self.handler.handle(self.subscriptions[chan_id], *message[1:])
            except websockets.ConnectionClosedError as error:
                if error.code == 1006:
                    self.on_open_event.clear()
                    reconnection = True
                    continue

                raise error

            break

    @_require_websocket_connection
    async def subscribe(self, channel, sub_id=None, **kwargs):
        if len(self.subscriptions) + len(self.pendings) == BfxWebsocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
            raise TooManySubscriptions("The client has reached the maximum number of subscriptions.")

        subscription = {
            **kwargs,

            "event": "subscribe",
            "channel": channel,
            "subId": sub_id or str(uuid.uuid4()),
        }

        self.pendings.append(subscription)

        await self.websocket.send(json.dumps(subscription))

    @_require_websocket_connection
    async def unsubscribe(self, chan_id):
        await self.websocket.send(json.dumps({
            "event": "unsubscribe",
            "chanId": chan_id
        }))

    @_require_websocket_connection
    async def close(self, code=1000, reason=str()):
        await self.websocket.close(code=code, reason=reason)

    def get_chan_id(self, sub_id):
        for subscription in self.subscriptions.values():
            if subscription["subId"] == sub_id:
                return subscription["chanId"]
