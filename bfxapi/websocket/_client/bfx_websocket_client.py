from typing import \
    TYPE_CHECKING, TypeVar, TypedDict,\
    Callable, Optional, Tuple, \
    List, Dict, Any

from logging import Logger

from datetime import datetime

from socket import gaierror

import \
    traceback, json, asyncio, \
    hmac, hashlib, random, \
    websockets

from websockets.exceptions import ConnectionClosedError

from websockets.legacy.client import connect as _websockets__connect

from bfxapi._utils.json_encoder import JSONEncoder

from bfxapi.websocket._handlers import \
    PublicChannelsHandler, AuthEventsHandler

from bfxapi.websocket._connection import Connection

from bfxapi.websocket._event_emitter import BfxEventEmitter

from bfxapi.websocket.exceptions import \
    InvalidAuthenticationCredentials, EventNotSupported, ZeroConnectionsError, \
    ReconnectionTimeoutError, OutdatedClientVersion

from .bfx_websocket_bucket import BfxWebSocketBucket

from .bfx_websocket_inputs import BfxWebSocketInputs

if TYPE_CHECKING:
    from asyncio import Task

    _T = TypeVar("_T", bound=Callable[..., None])

    _Credentials = TypedDict("_Credentials", \
        { "api_key": str, "api_secret": str, "filters": Optional[List[str]] })

    _Reconnection = TypedDict("_Reconnection",
        { "attempts": int, "reason": str, "timestamp": datetime })

_DEFAULT_LOGGER = Logger("bfxapi.websocket._client", level=0)

class BfxWebSocketClient(Connection, Connection.Authenticable):
    VERSION = BfxWebSocketBucket.VERSION

    MAXIMUM_CONNECTIONS_AMOUNT = 20

    __ONCE_EVENTS = [
        "open", "authenticated", "disconnection",
        *AuthEventsHandler.ONCE_EVENTS
    ]

    EVENTS = [
        "subscribed", "wss-error",
        *__ONCE_EVENTS,
        *PublicChannelsHandler.EVENTS,
        *AuthEventsHandler.ON_EVENTS
    ]

    def __init__(self,
                 host: str,
                 *,
                 credentials: Optional["_Credentials"] = None,
                 timeout: Optional[float] = 60 * 15,
                 logger: Logger = _DEFAULT_LOGGER) -> None:
        super().__init__(host)

        self.__credentials, self.__timeout, self.__logger = \
            credentials, timeout, logger

        self.__event_emitter = BfxEventEmitter(targets = \
            PublicChannelsHandler.ONCE_PER_SUBSCRIPTION + \
                ["subscribed"])

        self.__handler = AuthEventsHandler(\
            event_emitter=self.__event_emitter)

        self.__inputs = BfxWebSocketInputs(\
            handle_websocket_input=self.__handle_websocket_input)

        self.__buckets: Dict[BfxWebSocketBucket, Optional["Task"]] = { }

        self.__reconnection: Optional[_Reconnection] = None

        @self.__event_emitter.on("error")
        def error(exception: Exception) -> None:
            header = f"{type(exception).__name__}: {str(exception)}"

            stack_trace = traceback.format_exception( \
                type(exception), exception, exception.__traceback__)

            self.__logger.critical( \
                header + "\n" + str().join(stack_trace)[:-1])

    @property
    def inputs(self) -> BfxWebSocketInputs:
        return self.__inputs

    def run(self, connections: int = 5) -> None:
        return asyncio.run(self.start(connections))

    async def start(self, connections: int = 5) -> None:
        if connections == 0:
            self.__logger.info("With connections set to 0 it will not be possible to subscribe to any " \
                "public channel. Attempting a subscription will cause a ZeroConnectionsError to be thrown.")

        if connections > BfxWebSocketClient.MAXIMUM_CONNECTIONS_AMOUNT:
            self.__logger.warning(f"It is not safe to use more than {BfxWebSocketClient.MAXIMUM_CONNECTIONS_AMOUNT} " \
                f"buckets from the same connection ({connections} in use), the server could momentarily " \
                    "block the client with <429 Too Many Requests>.")

        for _ in range(connections):
            _bucket = BfxWebSocketBucket( \
                self._host, self.__event_emitter)

            self.__buckets.update( { _bucket: None })

        await self.__connect()

    #pylint: disable-next=too-many-branches,too-many-statements
    async def __connect(self) -> None:
        class _Delay:
            BACKOFF_MIN, BACKOFF_MAX = 1.92, 60.0

            BACKOFF_INITIAL = 5.0

            def __init__(self, backoff_factor: float) -> None:
                self.__backoff_factor = backoff_factor
                self.__backoff_delay = _Delay.BACKOFF_MIN
                self.__initial_delay = random.random() * _Delay.BACKOFF_INITIAL

            def next(self) -> float:
                _backoff_delay = self.peek()
                __backoff_delay = self.__backoff_delay * self.__backoff_factor
                self.__backoff_delay = min(__backoff_delay, _Delay.BACKOFF_MAX)

                return _backoff_delay

            def peek(self) -> float:
                return (self.__backoff_delay == _Delay.BACKOFF_MIN) \
                    and self.__initial_delay or self.__backoff_delay

            def reset(self) -> None:
                self.__backoff_delay = _Delay.BACKOFF_MIN

        _delay = _Delay(backoff_factor=1.618)

        _sleep: Optional["Task"] = None

        def _on_timeout():
            if not self.open:
                if _sleep:
                    _sleep.cancel()

        while True:
            if self.__reconnection:
                _sleep = asyncio.create_task( \
                    asyncio.sleep(_delay.next()))

                try:
                    await _sleep
                except asyncio.CancelledError:
                    raise ReconnectionTimeoutError("Connection has been offline for too long " \
                        f"without being able to reconnect (timeout: {self.__timeout}s).") \
                            from None

            try:
                await self.__connection()
            except (ConnectionClosedError, gaierror) as error:
                async def _cancel(task: "Task") -> None:
                    task.cancel()

                    try:
                        await task
                    except (ConnectionClosedError, gaierror) as _e:
                        if type(error) is not type(_e) or error.args != _e.args:
                            raise _e
                    except asyncio.CancelledError:
                        pass

                for bucket in self.__buckets:
                    if task := self.__buckets[bucket]:
                        self.__buckets[bucket] = None

                        await _cancel(task)

                if isinstance(error, ConnectionClosedError) and error.code in (1006, 1012):
                    if error.code == 1006:
                        self.__logger.error("Connection lost: no close frame " \
                            "received or sent (1006). Trying to reconnect...")

                    if error.code == 1012:
                        self.__logger.info("WSS server is about to restart, clients need " \
                            "to reconnect (server sent 20051). Reconnection attempt in progress...")

                    if self.__timeout is not None:
                        asyncio.get_event_loop().call_later(
                            self.__timeout, _on_timeout)

                    self.__reconnection = \
                        { "attempts": 1, "reason": error.reason, "timestamp": datetime.now() }

                    self._authentication = False

                    _delay.reset()
                elif isinstance(error, gaierror) and self.__reconnection:
                    self.__logger.warning(
                        f"_Reconnection attempt was unsuccessful (no.{self.__reconnection['attempts']}). " \
                            f"Next reconnection attempt in {_delay.peek():.2f} seconds. (at the moment " \
                                f"the client has been offline for {datetime.now() - self.__reconnection['timestamp']})")

                    self.__reconnection["attempts"] += 1
                else:
                    raise error

            if not self.__reconnection:
                self.__event_emitter.emit("disconnection",
                    self._websocket.close_code, \
                        self._websocket.close_reason)

                break

    async def __connection(self) -> None:
        async with _websockets__connect(self._host) as websocket:
            if self.__reconnection:
                self.__logger.info(f"_Reconnection attempt successful (no.{self.__reconnection['attempts']}): The " \
                    f"client has been offline for a total of {datetime.now() - self.__reconnection['timestamp']} " \
                        f"(connection lost on: {self.__reconnection['timestamp']:%d-%m-%Y at %H:%M:%S}).")

                self.__reconnection = None

            self._websocket = websocket

            self.__buckets = {
                bucket: asyncio.create_task(_c)
                    for bucket in self.__buckets
                        if (_c := bucket.connect())
            }

            if len(self.__buckets) == 0 or \
                    (await asyncio.gather(*[bucket.wait() for bucket in self.__buckets])):
                self.__event_emitter.emit("open")

            if self.__credentials:
                authentication = BfxWebSocketClient. \
                    __build_authentication_message(**self.__credentials)

                await self._websocket.send(authentication)

            async for message in self._websocket:
                message = json.loads(message)

                if isinstance(message, dict):
                    if message["event"] == "info" and "version" in message:
                        if BfxWebSocketClient.VERSION != message["version"]:
                            raise OutdatedClientVersion("Mismatch between the client version and the server " \
                                "version. Update the library to the latest version to continue (client version: " \
                                    f"{BfxWebSocketClient.VERSION}, server version: {message['version']}).")
                    elif message["event"] == "info" and message["code"] == 20051:
                        code, reason = 1012, "Stop/Restart WebSocket Server (please reconnect)."
                        rcvd = websockets.frames.Close(code=code, reason=reason)
                        raise ConnectionClosedError(rcvd=rcvd, sent=None)
                    elif message["event"] == "auth":
                        if message["status"] != "OK":
                            raise InvalidAuthenticationCredentials(
                                "Cannot authenticate with given API-KEY and API-SECRET.")

                        self.__event_emitter.emit("authenticated", message)

                        self._authentication = True
                    elif message["event"] == "error":
                        self.__event_emitter.emit("wss-error", message["code"], message["msg"])

                if isinstance(message, list) and \
                        message[0] == 0 and message[1] != Connection.HEARTBEAT:
                    self.__handler.handle(message[1], message[2])

    @Connection.require_websocket_connection
    async def subscribe(self,
                        channel: str,
                        sub_id: Optional[str] = None,
                        **kwargs: Any) -> None:
        if len(self.__buckets) == 0:
            raise ZeroConnectionsError("Unable to subscribe: " \
                "the number of connections must be greater than 0.")

        _buckets = list(self.__buckets.keys())

        counters = [ len(bucket.pendings) + len(bucket.subscriptions)
            for bucket in _buckets ]

        index = counters.index(min(counters))

        await _buckets[index] \
            .subscribe(channel, sub_id, **kwargs)

    @Connection.require_websocket_connection
    async def unsubscribe(self, sub_id: str) -> None:
        for bucket in self.__buckets:
            if bucket.has(sub_id=sub_id):
                await bucket.unsubscribe(sub_id=sub_id)

    @Connection.require_websocket_connection
    async def close(self, code: int = 1000, reason: str = str()) -> None:
        for bucket in self.__buckets:
            await bucket.close(code=code, reason=reason)

        if self._websocket.open:
            await self._websocket.close( \
                code=code, reason=reason)

    @Connection.Authenticable.require_websocket_authentication
    async def notify(self,
                     info: Any,
                     message_id: Optional[int] = None,
                     **kwargs: Any) -> None:
        await self._websocket.send(
            json.dumps([ 0, "n", message_id,
                { "type": "ucm-test", "info": info, **kwargs } ]))

    @Connection.Authenticable.require_websocket_authentication
    async def __handle_websocket_input(self, event: str, data: Any) -> None:
        await self._websocket.send(json.dumps(\
            [ 0, event, None, data], cls=JSONEncoder))

    def on(self, *events: str, callback: Optional["_T"] = None) -> Callable[["_T"], None]:
        for event in events:
            if event not in BfxWebSocketClient.EVENTS:
                raise EventNotSupported(f"Event <{event}> is not supported. To get a list " \
                    "of available events see BfxWebSocketClient.EVENTS.")

        def _register_events(function: "_T", events: Tuple[str, ...]) -> None:
            for event in events:
                if event in BfxWebSocketClient.__ONCE_EVENTS:
                    self.__event_emitter.once(event, function)
                else:
                    self.__event_emitter.on(event, function)

        if callback:
            _register_events(callback, events)

        def _handler(function: "_T") -> None:
            _register_events(function, events)

        return _handler

    @staticmethod
    def __build_authentication_message(api_key: str,
                                       api_secret: str,
                                       filters: Optional[List[str]] = None) -> str:
        message: Dict[str, Any] = \
            { "event": "auth", "filter": filters, "apiKey": api_key }

        message["authNonce"] = round(datetime.now().timestamp() * 1_000_000)

        message["authPayload"] = f"AUTH{message['authNonce']}"

        message["authSig"] = hmac.new(
            key=api_secret.encode("utf8"),
            msg=message["authPayload"].encode("utf8"),
            digestmod=hashlib.sha384
        ).hexdigest()

        return json.dumps(message)
