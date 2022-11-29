import json, asyncio, hmac, hashlib, time, uuid, websockets

from enum import Enum

from pyee.asyncio import AsyncIOEventEmitter

from .handlers import Channels, PublicChannelsHandler, AuthenticatedChannelsHandler

from .exceptions import ConnectionNotOpen, TooManySubscriptions, WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported, OutdatedClientVersion

from ..utils.logger import Formatter, CustomLogger

_HEARTBEAT = "hb"

def _require_websocket_connection(function):
    async def wrapper(self, *args, **kwargs):
        if self.websocket == None or self.websocket.open == False:
            raise ConnectionNotOpen("No open connection with the server.")
    
        await function(self, *args, **kwargs)

    return wrapper

class BfxWebsocketClient(object):
    VERSION = 2

    EVENTS = [
        "open", "subscribed", "authenticated", "wss-error",
        *PublicChannelsHandler.EVENTS,
        *AuthenticatedChannelsHandler.EVENTS
    ]

    def __init__(self, host, buckets=5, log_level = "ERROR", API_KEY=None, API_SECRET=None, filter=None):
        self.host, self.websocket, self.event_emitter = host, None, AsyncIOEventEmitter()

        self.event_emitter.add_listener("error", lambda message: self.logger.error(message))

        self.API_KEY, self.API_SECRET, self.filter, self.authentication = API_KEY, API_SECRET, filter, False

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        self.buckets = [ _BfxWebsocketBucket(self.host, self.event_emitter, self.__bucket_open_signal) for _ in range(buckets) ]

        self.inputs = _BfxWebsocketInputs(self.__handle_websocket_input)

        self.logger = CustomLogger("BfxWebsocketClient", logLevel=log_level)

    def run(self):
        return asyncio.run(self.start())

    async def start(self):
        tasks = [ bucket._connect(index) for index, bucket in enumerate(self.buckets) ]
        
        if self.API_KEY != None and self.API_SECRET != None:
            tasks.append(self.__connect(self.API_KEY, self.API_SECRET, self.filter))

        await asyncio.gather(*tasks)

    async def __connect(self, API_KEY, API_SECRET, filter=None):
        async for websocket in websockets.connect(self.host):
            self.websocket = websocket
            
            await self.__authenticate(API_KEY, API_SECRET, filter)

            try:
                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "auth":
                        if message["status"] == "OK":
                            self.event_emitter.emit("authenticated", message); self.authentication = True
                        else: raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])
                    elif isinstance(message, list) and (chanId := message[0]) == 0 and message[1] != _HEARTBEAT:
                        self.handler.handle(message[1], message[2])
            except websockets.ConnectionClosedError: continue
            finally: await self.websocket.wait_closed(); break

    async def __authenticate(self, API_KEY, API_SECRET, filter=None):
        data = { "event": "auth", "filter": filter, "apiKey": API_KEY }

        data["authNonce"] = int(time.time()) * 1000

        data["authPayload"] = "AUTH" + str(data["authNonce"])

        data["authSig"] = hmac.new(
            API_SECRET.encode("utf8"),
            data["authPayload"].encode("utf8"),
            hashlib.sha384 
        ).hexdigest()

        await self.websocket.send(json.dumps(data))

    async def subscribe(self, channel, **kwargs):
        counters = [ len(bucket.pendings) + len(bucket.subscriptions) for bucket in self.buckets ]

        index = counters.index(min(counters))

        await self.buckets[index]._subscribe(channel, **kwargs)

    async def unsubscribe(self, chanId):
        for bucket in self.buckets:
            if chanId in bucket.subscriptions.keys():
                await bucket._unsubscribe(chanId=chanId)

    async def close(self, code=1000, reason=str()):
        if self.websocket != None and self.websocket.open == True:
            await self.websocket.close(code=code, reason=reason)

        for bucket in self.buckets:
            await bucket._close(code=code, reason=reason)

    def __require_websocket_authentication(function):
        async def wrapper(self, *args, **kwargs):
            if self.authentication == False:
                raise WebsocketAuthenticationRequired("To perform this action you need to authenticate using your API_KEY and API_SECRET.")
        
            await _require_websocket_connection(function)(self, *args, **kwargs)

        return wrapper

    @__require_websocket_authentication
    async def notify(self, info, MESSAGE_ID=None, **kwargs):
        await self.websocket.send(json.dumps([ 0, "n", MESSAGE_ID, { "type": "ucm-test", "info": info, **kwargs } ]))

    @__require_websocket_authentication
    async def __handle_websocket_input(self, input, data):
        await self.websocket.send(json.dumps([ 0, input, None, data]))

    def __bucket_open_signal(self, index):
        if all(bucket.websocket != None and bucket.websocket.open == True for bucket in self.buckets):
            self.event_emitter.emit("open")

    def on(self, event, callback = None):
        if event not in BfxWebsocketClient.EVENTS:
            raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        if callback != None:
            return self.event_emitter.on(event, callback)

        def handler(function):
            self.event_emitter.on(event, function)
        return handler 

    def once(self, event, callback = None):
        if event not in BfxWebsocketClient.EVENTS:
            raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        if callback != None:
            return self.event_emitter.once(event, callback)

        def handler(function):
            self.event_emitter.once(event, function)
        return handler 

class _BfxWebsocketBucket(object):
    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter, __bucket_open_signal):
        self.host, self.event_emitter, self.__bucket_open_signal = host, event_emitter, __bucket_open_signal

        self.websocket, self.subscriptions, self.pendings = None, dict(), list()

        self.handler = PublicChannelsHandler(event_emitter=self.event_emitter)

    async def _connect(self, index):
        async for websocket in websockets.connect(self.host):
            self.websocket = websocket

            self.__bucket_open_signal(index)

            try:
                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "info" and "version" in message:
                        if BfxWebsocketClient.VERSION != message["version"]:
                            raise OutdatedClientVersion(f"Mismatch between the client version and the server version. Update the library to the latest version to continue (client version: {BfxWebsocketClient.VERSION}, server version: {message['version']}).")
                    elif isinstance(message, dict) and message["event"] == "subscribed" and (chanId := message["chanId"]):
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
            except websockets.ConnectionClosedError: continue
            finally: await self.websocket.wait_closed(); break

    @_require_websocket_connection
    async def _subscribe(self, channel, subId=None, **kwargs):
        if len(self.subscriptions) + len(self.pendings) == _BfxWebsocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
            raise TooManySubscriptions("The client has reached the maximum number of subscriptions.")

        subscription = {
            "event": "subscribe",
            "channel": channel,
            "subId": subId or str(uuid.uuid4()),

            **kwargs
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

class _BfxWebsocketInputs(object):
    def __init__(self, __handle_websocket_input):
        self.__handle_websocket_input = __handle_websocket_input

    async def order_new(self, data):
        await self.__handle_websocket_input("on", data)

    async def order_update(self, data):
        await self.__handle_websocket_input("ou", data)

    async def order_cancel(self, data):
        await self.__handle_websocket_input("oc", data)