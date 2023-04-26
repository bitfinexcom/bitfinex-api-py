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

class BfxWebSocketBucket:
    VERSION = 2

    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter, events_per_subscription):
        self.host, self.event_emitter, self.events_per_subscription = host, event_emitter, events_per_subscription
        self.websocket, self.subscriptions, self.pendings = None, {}, []
        self.on_open_event = asyncio.locks.Event()

        self.handler = PublicChannelsHandler(event_emitter=self.event_emitter, \
            events_per_subscription=self.events_per_subscription)

    async def connect(self):
        async def _connection():
            async with websockets.connect(self.host) as websocket:
                self.websocket = websocket
                self.on_open_event.set()
                await self.__recover_state()

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict):
                        if message["event"] == "subscribed" and (chan_id := message["chanId"]):
                            self.pendings = [ pending \
                                for pending in self.pendings if pending["subId"] != message["subId"] ]

                            self.subscriptions[chan_id] = message

                            sub_id = message["subId"]

                            if "subscribed" not in self.events_per_subscription.get(sub_id, []):
                                self.events_per_subscription.setdefault(sub_id, []).append("subscribed")
                                self.event_emitter.emit("subscribed", message)
                        elif message["event"] == "unsubscribed" and (chan_id := message["chanId"]):
                            if message["status"] == "OK":
                                del self.subscriptions[chan_id]
                        elif message["event"] == "error":
                            self.event_emitter.emit("wss-error", message["code"], message["msg"])

                    if isinstance(message, list):
                        if (chan_id := message[0]) and message[1] != _HEARTBEAT:
                            self.handler.handle(self.subscriptions[chan_id], *message[1:])

        try:
            await _connection()
        except websockets.exceptions.ConnectionClosedError as error:
            if error.code in (1006, 1012):
                self.on_open_event.clear()

    async def __recover_state(self):
        for pending in self.pendings:
            await self.websocket.send(json.dumps(pending))

        for _, subscription in self.subscriptions.items():
            await self.subscribe(sub_id=subscription.pop("subId"), **subscription)

        self.subscriptions.clear()

    @_require_websocket_connection
    async def subscribe(self, channel, sub_id=None, **kwargs):
        if len(self.subscriptions) + len(self.pendings) == BfxWebSocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
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
