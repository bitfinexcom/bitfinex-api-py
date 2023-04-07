from typing import cast

from collections import namedtuple

from datetime import datetime

import traceback, json, asyncio, hmac, hashlib, time, socket, random, websockets

from pyee.asyncio import AsyncIOEventEmitter

from .bfx_websocket_bucket import _HEARTBEAT, F, _require_websocket_connection, BfxWebsocketBucket

from .bfx_websocket_inputs import BfxWebsocketInputs
from ..handlers import PublicChannelsHandler, AuthenticatedChannelsHandler
from ..exceptions import WebsocketAuthenticationRequired, InvalidAuthenticationCredentials, EventNotSupported, \
    ZeroConnectionsError, OutdatedClientVersion

from ...utils.json_encoder import JSONEncoder

from ...utils.logger import ColorLogger, FileLogger

def _require_websocket_authentication(function: F) -> F:
    async def wrapper(self, *args, **kwargs):
        if hasattr(self, "authentication") and not self.authentication:
            raise WebsocketAuthenticationRequired("To perform this action you need to " \
                "authenticate using your API_KEY and API_SECRET.")

        await _require_websocket_connection(function)(self, *args, **kwargs)

    return cast(F, wrapper)

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

class BfxWebsocketClient:
    VERSION = BfxWebsocketBucket.VERSION

    MAXIMUM_CONNECTIONS_AMOUNT = 20

    EVENTS = [
        "open", "subscribed", "authenticated", "wss-error",
        *PublicChannelsHandler.EVENTS,
        *AuthenticatedChannelsHandler.EVENTS
    ]

    def __init__(self, host, credentials = None, log_filename = None, log_level = "INFO"):
        self.websocket, self.buckets, self.authentication = None, [], False

        self.host, self.credentials, self.event_emitter = host, credentials, AsyncIOEventEmitter()

        self.inputs = BfxWebsocketInputs(handle_websocket_input=self.__handle_websocket_input)

        self.handler = AuthenticatedChannelsHandler(event_emitter=self.event_emitter)

        if log_filename is None:
            self.logger = ColorLogger("BfxWebsocketClient", level=log_level)
        else: self.logger = FileLogger("BfxWebsocketClient", level=log_level, filename=log_filename)

        self.event_emitter.add_listener("error",
            lambda exception: self.logger.error(f"{type(exception).__name__}: {str(exception)}" + "\n" +
                str().join(traceback.format_exception(type(exception), exception, exception.__traceback__))[:-1])
        )

    def run(self, connections = 5):
        return asyncio.run(self.start(connections))

    async def start(self, connections = 5):
        if connections == 0:
            self.logger.info("With connections set to 0 it will not be possible to subscribe to any public channel. " \
                    "Attempting a subscription will cause a ZeroConnectionsError to be thrown.")

        if connections > BfxWebsocketClient.MAXIMUM_CONNECTIONS_AMOUNT:
            self.logger.warning(f"It is not safe to use more than {BfxWebsocketClient.MAXIMUM_CONNECTIONS_AMOUNT} " \
                    f"buckets from the same connection ({connections} in use), the server could momentarily " \
                        "block the client with <429 Too Many Requests>.")

        for _ in range(connections):
            self.buckets += [BfxWebsocketBucket(self.host, self.event_emitter)]

        tasks = [ bucket.connect() for bucket in self.buckets ] + [ self.__connect() ]

        await asyncio.gather(*tasks)

    #pylint: disable-next=too-many-statements
    async def __connect(self):
        Reconnection = namedtuple("Reconnection", ["status", "attempts", "timestamp"])

        reconnection, delay = Reconnection(status=False, attempts=0, timestamp=None), None

        async def _connection():
            nonlocal reconnection

            async with websockets.connect(self.host) as websocket:
                if reconnection.status:
                    self.logger.info(f"Reconnect attempt successful (attempt no.{reconnection.attempts}): The " \
                        f"client has been offline for a total of {datetime.now() - reconnection.timestamp} " \
                            f"(connection lost at: {reconnection.timestamp:%d-%m-%Y at %H:%M:%S}).")

                    reconnection = Reconnection(status=False, attempts=0, timestamp=None)

                self.websocket, self.authentication = websocket, False

                if len(self.buckets) == 0 or \
                        (await asyncio.gather(*[bucket.on_open_event.wait() for bucket in self.buckets])):
                    self.event_emitter.emit("open")

                if self.credentials:
                    await self.__authenticate(**self.credentials)

                async for message in websocket:
                    message = json.loads(message)

                    if isinstance(message, dict):
                        if message["event"] == "info" and "version" in message:
                            if BfxWebsocketClient.VERSION != message["version"]:
                                raise OutdatedClientVersion("Mismatch between the client version and the server " \
                                    "version. Update the library to the latest version to continue (client version: " \
                                        f"{BfxWebsocketClient.VERSION}, server version: {message['version']}).")
                        elif message["event"] == "info" and message["code"] == 20051:
                            rcvd = websockets.frames.Close(code=1012,
                                reason="Stop/Restart Websocket Server (please reconnect).")

                            raise websockets.ConnectionClosedError(rcvd=rcvd, sent=None)
                        elif message["event"] == "auth":
                            if message["status"] != "OK":
                                raise InvalidAuthenticationCredentials(
                                    "Cannot authenticate with given API-KEY and API-SECRET.")

                            self.event_emitter.emit("authenticated", message)

                            self.authentication = True
                        elif message["event"] == "error":
                            self.event_emitter.emit("wss-error", message["code"], message["msg"])

                    if isinstance(message, list):
                        if message[0] == 0 and message[1] != _HEARTBEAT:
                            self.handler.handle(message[1], message[2])

        while True:
            if reconnection.status:
                await asyncio.sleep(delay.next())

            try:
                await _connection()
            except (websockets.ConnectionClosedError, socket.gaierror) as error:
                if isinstance(error, websockets.ConnectionClosedError) and error.code in (1006, 1012):
                    if error.code == 1006:
                        self.logger.error("Connection lost: no close frame received " \
                            "or sent (1006). Attempting to reconnect...")

                    if error.code == 1012:
                        self.logger.info("WSS server is about to restart, reconnection " \
                            "required (client received 20051). Attempt in progress...")

                    reconnection = Reconnection(status=True, attempts=1, timestamp=datetime.now())

                    delay = _Delay(backoff_factor=1.618)
                elif isinstance(error, socket.gaierror) and reconnection.status:
                    self.logger.warning(f"Reconnection attempt no.{reconnection.attempts} has failed. " \
                        f"Next reconnection attempt in ~{round(delay.peek()):.1f} seconds. (at the moment " \
                            f"the client has been offline for {datetime.now() - reconnection.timestamp})")

                    reconnection = reconnection._replace(attempts=reconnection.attempts + 1)
                else: raise error

            if not reconnection.status:
                break

    async def __authenticate(self, api_key, api_secret, filters=None):
        data = { "event": "auth", "filter": filters, "apiKey": api_key }

        data["authNonce"] = str(round(time.time() * 1_000_000))

        data["authPayload"] = "AUTH" + data["authNonce"]

        data["authSig"] = hmac.new(
            api_secret.encode("utf8"),
            data["authPayload"].encode("utf8"),
            hashlib.sha384
        ).hexdigest()

        await self.websocket.send(json.dumps(data))

    async def subscribe(self, channel, **kwargs):
        if len(self.buckets) == 0:
            raise ZeroConnectionsError("Unable to subscribe: the number of connections must be greater than 0.")

        counters = [ len(bucket.pendings) + len(bucket.subscriptions) for bucket in self.buckets ]

        index = counters.index(min(counters))

        await self.buckets[index].subscribe(channel, **kwargs)

    async def unsubscribe(self, sub_id):
        for bucket in self.buckets:
            if (chan_id := bucket.get_chan_id(sub_id)):
                await bucket.unsubscribe(chan_id=chan_id)

    async def close(self, code=1000, reason=str()):
        if self.websocket is not None and self.websocket.open:
            await self.websocket.close(code=code, reason=reason)

        for bucket in self.buckets:
            await bucket.close(code=code, reason=reason)

    @_require_websocket_authentication
    async def notify(self, info, message_id=None, **kwargs):
        await self.websocket.send(json.dumps([ 0, "n", message_id, { "type": "ucm-test", "info": info, **kwargs } ]))

    @_require_websocket_authentication
    async def __handle_websocket_input(self, event, data):
        await self.websocket.send(json.dumps([ 0, event, None, data], cls=JSONEncoder))

    def on(self, *events, callback = None):
        for event in events:
            if event not in BfxWebsocketClient.EVENTS:
                raise EventNotSupported(f"Event <{event}> is not supported. To get a list " \
                            "of available events print BfxWebsocketClient.EVENTS")

        if callback is not None:
            for event in events:
                self.event_emitter.on(event, callback)

        if callback is None:
            def handler(function):
                for event in events:
                    self.event_emitter.on(event, function)

            return handler

    def once(self, *events, callback = None):
        for event in events:
            if event not in BfxWebsocketClient.EVENTS:
                raise EventNotSupported(f"Event <{event}> is not supported. To get a list " \
                            "of available events print BfxWebsocketClient.EVENTS")

        if callback is not None:
            for event in events:
                self.event_emitter.once(event, callback)

        if callback is None:
            def handler(function):
                for event in events:
                    self.event_emitter.once(event, function)

            return handler
