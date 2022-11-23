import json, asyncio, hmac, hashlib, time, uuid, websockets

from enum import Enum

from pyee.asyncio import AsyncIOEventEmitter

from .handlers import Channels, PublicChannelsHandler, AuthenticatedChannelsHandler

from .exceptions import ConnectionNotOpen, TooManySubscriptions, WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported, OutdatedClientVersion

from ..utils.logger import Formatter, CustomLogger

HEARTBEAT = "hb"

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

    def __init__(self, host, buckets=5, log_level = "INFO", API_KEY=None, API_SECRET=None):
        self.host, self.websocket, self.event_emitter = host, None, AsyncIOEventEmitter()

        self.API_KEY, self.API_SECRET, self.authentication = API_KEY, API_SECRET, False

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        self.buckets = [ _BfxWebsocketBucket(self.host, self.event_emitter, self.__bucket_open_signal) for _ in range(buckets) ]

        self.logger = CustomLogger("BfxWebsocketClient", logLevel=log_level)

    async def start(self):
        tasks = [ bucket._connect(index) for index, bucket in enumerate(self.buckets) ]
        
        if self.API_KEY != None and self.API_SECRET != None:
            tasks.append(self.__connect(self.API_KEY, self.API_SECRET))

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
                    elif isinstance(message, list) and (chanId := message[0]) == 0 and message[1] != HEARTBEAT:
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
        counters = [ len(bucket.pendings) + len(bucket.chanIds) for bucket in self.buckets ]

        index = counters.index(min(counters))

        await self.buckets[index]._subscribe(channel, **kwargs)

    async def unsubscribe(self, chanId):
        for bucket in self.buckets:
            if chanId in bucket.chanIds.keys():
                await bucket._unsubscribe(chanId=chanId)

    async def close(self, code=1000, reason=str()):
        if self.websocket != None and self.websocket.open == True:
            await self.websocket.close(code=code, reason=reason)

        for bucket in self.buckets:
            await bucket.close(code=code, reason=reason)

    def __require_websocket_authentication(function):
        @_require_websocket_connection
        async def wrapper(self, *args, **kwargs):
            if self.authentication == False:
                raise WebsocketAuthenticationRequired("To perform this action you need to authenticate using your API_KEY and API_SECRET.")
        
            await function(self, *args, **kwargs)

        return wrapper

    def __bucket_open_signal(self, index):
        if all(bucket.websocket != None and bucket.websocket.open == True for bucket in self.buckets):
            self.event_emitter.emit("open")

    def on(self, event):
        if event not in BfxWebsocketClient.EVENTS:
            raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        def handler(function):
            self.event_emitter.on(event, function)

        return handler 

    def once(self, event):
        if event not in BfxWebsocketClient.EVENTS:
            raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        def handler(function):
            self.event_emitter.once(event, function)

        return handler 

class _BfxWebsocketBucket(object):
    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host, event_emitter, __bucket_open_signal):
        self.host, self.event_emitter, self.__bucket_open_signal = host, event_emitter, __bucket_open_signal

        self.websocket, self.chanIds, self.pendings = None, dict(), list()

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
                        self.chanIds[chanId] = message
                        self.event_emitter.emit("subscribed", message)
                    elif isinstance(message, dict) and message["event"] == "unsubscribed" and (chanId := message["chanId"]):
                        if message["status"] == "OK":
                            del self.chanIds[chanId]
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])
                    elif isinstance(message, list) and (chanId := message[0]) and message[1] != HEARTBEAT:
                        self.handler.handle(self.chanIds[chanId], *message[1:])
            except websockets.ConnectionClosedError: continue
            finally: await self.websocket.wait_closed(); break

    @_require_websocket_connection
    async def _subscribe(self, channel, subId=None, **kwargs):
        if len(self.chanIds) + len(self.pendings) == _BfxWebsocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
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
    async def close(self, code=1000, reason=str()):
        await self.websocket.close(code=code, reason=reason)

class Errors(int, Enum):
    ERR_UNK = 10000
    ERR_GENERIC = 10001
    ERR_CONCURRENCY = 10008
    ERR_PARAMS = 10020
    ERR_CONF_FAIL = 10050
    ERR_AUTH_FAIL = 10100
    ERR_AUTH_PAYLOAD = 10111
    ERR_AUTH_SIG = 10112
    ERR_AUTH_HMAC = 10113
    ERR_AUTH_NONCE = 10114
    ERR_UNAUTH_FAIL = 10200
    ERR_SUB_FAIL = 10300
    ERR_SUB_MULTI = 10301
    ERR_UNSUB_FAIL = 10400
    ERR_READY = 11000