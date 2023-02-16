import json, uuid, websockets

from typing import Literal, TypeVar, Callable, cast

from ..handlers import PublicChannelsHandler

from ..exceptions import ConnectionNotOpen, TooManySubscriptions, OutdatedClientVersion

_HEARTBEAT = "hb"

F = TypeVar("F", bound=Callable[..., Literal[None]])

def _require_websocket_connection(function: F) -> F:
    async def wrapper(self, *args, **kwargs):
        if self.websocket == None or self.websocket.open == False:
            raise ConnectionNotOpen("No open connection with the server.")
    
        await function(self, *args, **kwargs)

    return cast(F, wrapper)

class BfxWebsocketBucket(object):
    VERSION = 2

    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter, on_open_event):
        self.host, self.event_emitter, self.on_open_event = host, event_emitter, on_open_event

        self.websocket, self.subscriptions, self.pendings = None, dict(), list()

        self.handler = PublicChannelsHandler(event_emitter=self.event_emitter)

    async def _connect(self, index):
        reconnection = False

        async for websocket in websockets.connect(self.host):
            self.websocket = websocket

            if reconnection == True or (reconnection := False):
                for pending in self.pendings:
                    await self.websocket.send(json.dumps(pending))

                for _, subscription in self.subscriptions.items():
                    await self._subscribe(**subscription)

                self.subscriptions.clear()

            self.on_open_event.set()

            try:
                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "subscribed" and (chanId := message["chanId"]):
                        self.pendings = [ pending for pending in self.pendings if pending["subId"] != message["subId"] ]
                        self.subscriptions[chanId] = message
                        self.event_emitter.emit("subscribed", message)
                    elif isinstance(message, dict) and message["event"] == "unsubscribed" and (chanId := message["chanId"]):
                        if message["status"] == "OK":
                            del self.subscriptions[chanId]
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])
                    elif isinstance(message, list) and (chanId := message[0]) and message[1] != _HEARTBEAT:
                        self.handler.handle(self.subscriptions[chanId], *message[1:])
            except websockets.ConnectionClosedError: 
                self.on_open_event.clear()
                reconnection = True 
                continue
            
            break

    @_require_websocket_connection
    async def _subscribe(self, channel, subId=None, **kwargs):
        if len(self.subscriptions) + len(self.pendings) == BfxWebsocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
            raise TooManySubscriptions("The client has reached the maximum number of subscriptions.")

        subscription = {
            **kwargs,

            "event": "subscribe",
            "channel": channel,
            "subId": subId or str(uuid.uuid4()),
        }

        self.pendings.append(subscription)

        await self.websocket.send(json.dumps(subscription))

    @_require_websocket_connection
    async def _unsubscribe(self, chanId):
        await self.websocket.send(json.dumps({
            "event": "unsubscribe",
            "chanId": chanId
        }))

    @_require_websocket_connection
    async def _close(self, code=1000, reason=str()):
        await self.websocket.close(code=code, reason=reason)