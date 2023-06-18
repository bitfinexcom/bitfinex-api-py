import asyncio, json, uuid, websockets

from .._handlers import PublicChannelsHandler

from ..exceptions import ConnectionNotOpen, TooManySubscriptions

def require_websocket_connection(function):
    async def wrapper(self, *args, **kwargs):
        if self.websocket is None or not self.websocket.open:
            raise ConnectionNotOpen("No open connection with the server.")

        await function(self, *args, **kwargs)

    return wrapper

class BfxWebSocketBucket:
    VERSION = 2

    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter):
        self.host, self.websocket, self.event_emitter = \
            host, None, event_emitter

        self.condition, self.subscriptions, self.pendings = \
            asyncio.locks.Condition(), {}, []

        self.handler = PublicChannelsHandler(event_emitter=self.event_emitter)

    async def connect(self):
        async with websockets.connect(self.host) as websocket:
            self.websocket = websocket

            await self.__recover_state()

            async with self.condition:
                self.condition.notify()

            async for message in websocket:
                message = json.loads(message)

                if isinstance(message, dict):
                    if message["event"] == "subscribed" and (chan_id := message["chanId"]):
                        self.pendings = [ pending \
                            for pending in self.pendings if pending["subId"] != message["subId"] ]

                        self.subscriptions[chan_id] = message

                        self.event_emitter.emit("subscribed", message)
                    elif message["event"] == "unsubscribed" and (chan_id := message["chanId"]):
                        if message["status"] == "OK":
                            del self.subscriptions[chan_id]
                    elif message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])

                if isinstance(message, list):
                    if (chan_id := message[0]) and message[1] != "hb":
                        self.handler.handle(self.subscriptions[chan_id], message[1:])

    async def __recover_state(self):
        for pending in self.pendings:
            await self.websocket.send(json.dumps(pending))

        for _, subscription in self.subscriptions.items():
            await self.subscribe(sub_id=subscription.pop("subId"), **subscription)

        self.subscriptions.clear()

    @require_websocket_connection
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

    @require_websocket_connection
    async def unsubscribe(self, chan_id):
        await self.websocket.send(json.dumps({
            "event": "unsubscribe",
            "chanId": chan_id
        }))

    @require_websocket_connection
    async def close(self, code=1000, reason=str()):
        await self.websocket.close(code=code, reason=reason)

    def get_chan_id(self, sub_id):
        for subscription in self.subscriptions.values():
            if subscription["subId"] == sub_id:
                return subscription["chanId"]

    async def wait(self):
        async with self.condition:
            await self.condition.wait_for(
                lambda: self.websocket is not None and \
                    self.websocket.open)