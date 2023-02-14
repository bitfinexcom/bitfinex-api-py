import traceback, json, asyncio, hmac, hashlib, time, websockets

from typing import cast

from pyee.asyncio import AsyncIOEventEmitter

from .bfx_websocket_bucket import _HEARTBEAT, F, _require_websocket_connection, BfxWebsocketBucket

from .bfx_websocket_inputs import BfxWebsocketInputs
from ..handlers import PublicChannelsHandler, AuthenticatedChannelsHandler
from ..exceptions import WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported

from ...utils.JSONEncoder import JSONEncoder

from ...utils.logger import Formatter, CustomLogger

def _require_websocket_authentication(function: F) -> F:
    async def wrapper(self, *args, **kwargs):
        if self.authentication == False:
            raise WebsocketAuthenticationRequired("To perform this action you need to authenticate using your API_KEY and API_SECRET.")
    
        await _require_websocket_connection(function)(self, *args, **kwargs)

    return cast(F, wrapper)

class BfxWebsocketClient(object):
    VERSION = BfxWebsocketBucket.VERSION

    MAXIMUM_BUCKETS_AMOUNT = 20

    EVENTS = [
        "open", "subscribed", "authenticated", "wss-error",
        *PublicChannelsHandler.EVENTS,
        *AuthenticatedChannelsHandler.EVENTS
    ]

    def __init__(self, host, API_KEY = None, API_SECRET = None, filter = None, buckets = 5, log_level = "WARNING"):
        self.host, self.websocket, self.event_emitter = host, None, AsyncIOEventEmitter()

        self.API_KEY, self.API_SECRET, self.filter, self.authentication = API_KEY, API_SECRET, filter, False

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        self.logger = CustomLogger("BfxWebsocketClient", logLevel=log_level)

        self.event_emitter.add_listener("error", 
            lambda exception: self.logger.error(f"{type(exception).__name__}: {str(exception)}" + "\n" + 
                str().join(traceback.format_exception(type(exception), exception, exception.__traceback__))[:-1])
        )

        if buckets > BfxWebsocketClient.MAXIMUM_BUCKETS_AMOUNT:
            self.logger.warning(f"It is not safe to use more than {BfxWebsocketClient.MAXIMUM_BUCKETS_AMOUNT} buckets from the same \
                connection ({buckets} in use), the server could momentarily block the client with <429 Too Many Requests>.")

        self.buckets = [ BfxWebsocketBucket(self.host, self.event_emitter, self.__bucket_open_signal) for _ in range(buckets) ]

        self.inputs = BfxWebsocketInputs(self.__handle_websocket_input)

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

    @_require_websocket_authentication
    async def notify(self, info, MESSAGE_ID=None, **kwargs):
        await self.websocket.send(json.dumps([ 0, "n", MESSAGE_ID, { "type": "ucm-test", "info": info, **kwargs } ]))

    @_require_websocket_authentication
    async def __handle_websocket_input(self, input, data):
        await self.websocket.send(json.dumps([ 0, input, None, data], cls=JSONEncoder))

    def __bucket_open_signal(self, index):
        if all(bucket.websocket != None and bucket.websocket.open == True for bucket in self.buckets):
            self.event_emitter.emit("open")

    def on(self, *events, callback = None):
        for event in events:
            if event not in BfxWebsocketClient.EVENTS:
                raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        if callback != None:
            for event in events:
                self.event_emitter.on(event, callback)

        if callback == None:
            def handler(function):
                for event in events:
                    self.event_emitter.on(event, function)

            return handler 

    def once(self, *events, callback = None):
        for event in events:
            if event not in BfxWebsocketClient.EVENTS:
                raise EventNotSupported(f"Event <{event}> is not supported. To get a list of available events print BfxWebsocketClient.EVENTS")

        if callback != None:
            for event in events:
                self.event_emitter.once(event, callback)

        if callback == None:
            def handler(function):
                for event in events:
                    self.event_emitter.once(event, function)

            return handler 