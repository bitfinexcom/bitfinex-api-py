import traceback, json, asyncio, hmac, hashlib, time, websockets

from typing import cast

from collections import namedtuple

from datetime import datetime

from pyee.asyncio import AsyncIOEventEmitter

from .bfx_websocket_bucket import _HEARTBEAT, F, _require_websocket_connection, BfxWebsocketBucket

from .bfx_websocket_inputs import BfxWebsocketInputs
from ..handlers import PublicChannelsHandler, AuthenticatedChannelsHandler
from ..exceptions import WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported, OutdatedClientVersion

from ...utils.JSONEncoder import JSONEncoder

from ...utils.logger import Formatter, CustomLogger

def _require_websocket_authentication(function: F) -> F:
    async def wrapper(self, *args, **kwargs):
        if hasattr(self, "authentication") and self.authentication == False:
            raise WebsocketAuthenticationRequired("To perform this action you need to authenticate using your API_KEY and API_SECRET.")
    
        await _require_websocket_connection(function)(self, *args, **kwargs)

    return cast(F, wrapper)

class BfxWebsocketClient(object):
    VERSION = BfxWebsocketBucket.VERSION

    MAXIMUM_CONNECTIONS_AMOUNT = 20

    EVENTS = [
        "open", "subscribed", "authenticated", "wss-error",
        *PublicChannelsHandler.EVENTS,
        *AuthenticatedChannelsHandler.EVENTS
    ]

    def __init__(self, host, API_KEY = None, API_SECRET = None, filter = None, log_level = "WARNING"):
        self.host, self.websocket, self.event_emitter = host, None, AsyncIOEventEmitter()

        self.API_KEY, self.API_SECRET, self.filter = API_KEY, API_SECRET, filter

        self.inputs = BfxWebsocketInputs(handle_websocket_input=self.__handle_websocket_input)

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        self.logger = CustomLogger("BfxWebsocketClient", logLevel=log_level)

        self.event_emitter.add_listener("error", 
            lambda exception: self.logger.error(f"{type(exception).__name__}: {str(exception)}" + "\n" + 
                str().join(traceback.format_exception(type(exception), exception, exception.__traceback__))[:-1])
        )

    def run(self, connections = 5):
        return asyncio.run(self.start(connections))

    async def start(self, connections = 5):
        if connections > BfxWebsocketClient.MAXIMUM_CONNECTIONS_AMOUNT:
            self.logger.warning(f"It is not safe to use more than {BfxWebsocketClient.MAXIMUM_CONNECTIONS_AMOUNT} buckets from the same " +
                f"connection ({connections} in use), the server could momentarily block the client with <429 Too Many Requests>.")

        self.on_open_events = [ asyncio.Event() for _ in range(connections)  ]

        self.buckets = [ 
            BfxWebsocketBucket(self.host, self.event_emitter, self.on_open_events[index]) 
                for index in range(connections) 
        ]

        tasks = [ bucket._connect(index) for index, bucket in enumerate(self.buckets) ]
        
        tasks.append(self.__connect(self.API_KEY, self.API_SECRET, self.filter))

        await asyncio.gather(*tasks)

    async def __connect(self, API_KEY, API_SECRET, filter=None):
        Reconnection = namedtuple("Reconnection", ["status", "code", "timestamp"])

        reconnection = Reconnection(status=False, code=0, timestamp=None)

        async for websocket in websockets.connect(self.host):
            self.websocket, self.authentication = websocket, False

            if (await asyncio.gather(*[ on_open_event.wait() for on_open_event in self.on_open_events ])):
                self.event_emitter.emit("open")

            if self.API_KEY != None and self.API_SECRET != None:
                await self.__authenticate(API_KEY=API_KEY, API_SECRET=API_SECRET, filter=filter)

            try:
                async for message in websocket:
                    if reconnection.status == True:
                        self.logger.warning(f"Reconnect Attempt Successful (error <{reconnection.code}>): The " +
                            f"client has been offline for a total of {datetime.now() - reconnection.timestamp} " +
                                f"(first reconnection attempt: {reconnection.timestamp:%d-%m-%Y at %H:%M:%S}).")

                        reconnection = Reconnection(status=False, code=0, timestamp=None)

                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "info" and "version" in message:
                        if BfxWebsocketClient.VERSION != message["version"]:
                            raise OutdatedClientVersion(f"Mismatch between the client version and the server version. " +
                                f"Update the library to the latest version to continue (client version: {BfxWebsocketClient.VERSION}, " +
                                    f"server version: {message['version']}).")
                    elif isinstance(message, dict) and message["event"] == "auth":
                        if message["status"] == "OK":
                            self.event_emitter.emit("authenticated", message); self.authentication = True
                        else: raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])
                    elif isinstance(message, list) and (chanId := message[0]) == 0 and message[1] != _HEARTBEAT:
                        self.handler.handle(message[1], message[2])
            except websockets.ConnectionClosedError as error:
                self.logger.error(f"Connection terminated due to an error (status code: <{error.code}>) -> {str(error)}. Attempting to reconnect...")
                reconnection = Reconnection(status=True, code=error.code, timestamp=datetime.now()); 
                continue
                        
            if reconnection.status == False:
                await self.websocket.wait_closed(); break

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