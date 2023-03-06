import traceback, json, asyncio, hmac, hashlib, time, websockets, socket, random

from typing import cast

from collections import namedtuple

from datetime import datetime

from pyee.asyncio import AsyncIOEventEmitter

from .bfx_websocket_bucket import _HEARTBEAT, F, _require_websocket_connection, BfxWebsocketBucket

from .bfx_websocket_inputs import BfxWebsocketInputs
from ..handlers import PublicChannelsHandler, AuthenticatedChannelsHandler
from ..exceptions import WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported, OutdatedClientVersion

from ...utils.JSONEncoder import JSONEncoder

from ...utils.logger import ColorLogger, FileLogger

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

    def __init__(self, host, credentials = None, log_filename = None, log_level = "INFO"):
        self.websocket = None

        self.host, self.credentials, self.event_emitter = host, credentials, AsyncIOEventEmitter()

        self.inputs = BfxWebsocketInputs(handle_websocket_input=self.__handle_websocket_input)

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        if log_filename == None:
            self.logger = ColorLogger("BfxWebsocketClient", level=log_level)
        else: self.logger = FileLogger("BfxWebsocketClient", level=log_level, filename=log_filename)

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
        
        tasks.append(self.__connect(self.credentials))

        await asyncio.gather(*tasks)

    async def __connect(self, credentials = None):
        Reconnection = namedtuple("Reconnection", ["status", "attempts", "timestamp"])

        reconnection, delay = Reconnection(status=False, attempts=0, timestamp=None), None

        async def _connection():
            nonlocal reconnection

            async with websockets.connect(self.host) as websocket:
                if reconnection.status == True:
                    self.logger.info(f"Reconnect attempt successful (attempt no.{reconnection.attempts}): The " +
                        f"client has been offline for a total of {datetime.now() - reconnection.timestamp} " +
                            f"(connection lost at: {reconnection.timestamp:%d-%m-%Y at %H:%M:%S}).")

                    reconnection = Reconnection(status=False, attempts=0, timestamp=None)

                self.websocket, self.authentication = websocket, False

                if await asyncio.gather(*[on_open_event.wait() for on_open_event in self.on_open_events]):
                    self.event_emitter.emit("open")

                if self.credentials:
                    await self.__authenticate(**self.credentials)

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict) and message["event"] == "info" and "version" in message:
                        if BfxWebsocketClient.VERSION != message["version"]:
                            raise OutdatedClientVersion(f"Mismatch between the client version and the server version. " +
                                f"Update the library to the latest version to continue (client version: {BfxWebsocketClient.VERSION}, " +
                                    f"server version: {message['version']}).")
                    elif isinstance(message, dict) and message["event"] == "info" and message["code"] == 20051:
                        rcvd = websockets.frames.Close(code=1012, reason="Stop/Restart Websocket Server (please reconnect).")

                        raise websockets.ConnectionClosedError(rcvd=rcvd, sent=None)
                    elif isinstance(message, dict) and message["event"] == "auth":
                        if message["status"] == "OK":
                            self.event_emitter.emit("authenticated", message); self.authentication = True
                        else: raise InvalidAuthenticationCredentials("Cannot authenticate with given API-KEY and API-SECRET.")
                    elif isinstance(message, dict) and message["event"] == "error":
                        self.event_emitter.emit("wss-error", message["code"], message["msg"])
                    elif isinstance(message, list) and (chanId := message[0]) == 0 and message[1] != _HEARTBEAT:
                        self.handler.handle(message[1], message[2])

        class _Delay:
            BACKOFF_MIN, BACKOFF_MAX = 1.92, 60.0

            BACKOFF_INITIAL = 5.0

            def __init__(self, backoff_factor):
                self.__backoff_factor = backoff_factor
                self.__backoff_delay = _Delay.BACKOFF_MIN
                self.__initial_delay = random.random() * _Delay.BACKOFF_INITIAL

            def next(self):
                backoff_delay = self.peek()
                __backoff_delay = self.__backoff_delay * self.__backoff_factor
                self.__backoff_delay = min(__backoff_delay, _Delay.BACKOFF_MAX)

                return backoff_delay
            
            def peek(self):
                return (self.__backoff_delay == _Delay.BACKOFF_MIN) \
                    and self.__initial_delay or self.__backoff_delay

        while True:
            if reconnection.status == True:
                await asyncio.sleep(delay.next())

            try:
                await _connection()
            except (websockets.ConnectionClosedError, socket.gaierror) as error:
                if isinstance(error, websockets.ConnectionClosedError) and (error.code == 1006 or error.code == 1012):                    
                    if error.code == 1006:
                        self.logger.error("Connection lost: no close frame received " 
                            + "or sent (1006). Attempting to reconnect...")

                    if error.code == 1012:
                        self.logger.info("WSS server is about to restart, reconnection "
                            + "required (client received 20051). Attempt in progress...")
                    
                    reconnection = Reconnection(status=True, attempts=1, timestamp=datetime.now()); 
                
                    delay = _Delay(backoff_factor=1.618)
                elif isinstance(error, socket.gaierror) and reconnection.status == True:
                    self.logger.warning(f"Reconnection attempt no.{reconnection.attempts} has failed. "
                        + f"Next reconnection attempt in ~{round(delay.peek()):.1f} seconds." 
                            + f"(at the moment the client has been offline for {datetime.now() - reconnection.timestamp})")

                    reconnection = reconnection._replace(attempts=reconnection.attempts + 1)
                else: raise error

            if reconnection.status == False:
                break

    async def __authenticate(self, API_KEY, API_SECRET, filters=None):
        data = { "event": "auth", "filter": filters, "apiKey": API_KEY }

        data["authNonce"] = str(round(time.time() * 1_000_000))

        data["authPayload"] = "AUTH" + data["authNonce"]

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

    async def unsubscribe(self, subId):
        for bucket in self.buckets:
            if (chanId := bucket._get_chan_id(subId)):
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