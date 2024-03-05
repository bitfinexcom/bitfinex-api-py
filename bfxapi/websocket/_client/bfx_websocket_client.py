import asyncio
import json
import random
import traceback
from asyncio import Task
from datetime import datetime
from logging import Logger
from socket import gaierror
from typing import Any, Dict, List, Optional, TypedDict

import websockets
import websockets.client
from websockets.exceptions import ConnectionClosedError, InvalidStatusCode

from bfxapi._utils.json_encoder import JSONEncoder
from bfxapi.exceptions import InvalidCredentialError
from bfxapi.websocket._connection import Connection
from bfxapi.websocket._event_emitter import BfxEventEmitter
from bfxapi.websocket._handlers import AuthEventsHandler
from bfxapi.websocket.exceptions import (
    ReconnectionTimeoutError,
    SubIdError,
    UnknownChannelError,
    UnknownSubscriptionError,
    VersionMismatchError,
)

from .bfx_websocket_bucket import BfxWebSocketBucket
from .bfx_websocket_inputs import BfxWebSocketInputs

_Credentials = TypedDict(
    "_Credentials", {"api_key": str, "api_secret": str, "filters": Optional[List[str]]}
)

_Reconnection = TypedDict(
    "_Reconnection", {"attempts": int, "reason": str, "timestamp": datetime}
)

_DEFAULT_LOGGER = Logger("bfxapi.websocket._client", level=0)


class _Delay:
    __BACKOFF_MIN = 1.92

    __BACKOFF_MAX = 60.0

    def __init__(self, backoff_factor: float) -> None:
        self.__backoff_factor = backoff_factor
        self.__backoff_delay = _Delay.__BACKOFF_MIN
        self.__initial_delay = random.uniform(1.0, 5.0)

    def next(self) -> float:
        _backoff_delay = self.peek()
        __backoff_delay = _backoff_delay * self.__backoff_factor
        self.__backoff_delay = min(__backoff_delay, _Delay.__BACKOFF_MAX)

        return _backoff_delay

    def peek(self) -> float:
        return (
            (self.__backoff_delay == _Delay.__BACKOFF_MIN)
            and self.__initial_delay
            or self.__backoff_delay
        )

    def reset(self) -> None:
        self.__backoff_delay = _Delay.__BACKOFF_MIN


class BfxWebSocketClient(Connection):
    def __init__(
        self,
        host: str,
        *,
        credentials: Optional[_Credentials] = None,
        timeout: Optional[int] = 60 * 15,
        logger: Logger = _DEFAULT_LOGGER,
    ) -> None:
        super().__init__(host)

        self.__credentials, self.__timeout, self.__logger = credentials, timeout, logger

        self.__buckets: Dict[BfxWebSocketBucket, Optional[Task]] = {}

        self.__reconnection: Optional[_Reconnection] = None

        self.__event_emitter = BfxEventEmitter(loop=None)

        self.__handler = AuthEventsHandler(event_emitter=self.__event_emitter)

        self.__inputs = BfxWebSocketInputs(
            handle_websocket_input=self.__handle_websocket_input
        )

        @self.__event_emitter.listens_to("error")
        def error(exception: Exception) -> None:
            header = f"{type(exception).__name__}: {str(exception)}"

            stack_trace = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )

            self.__logger.critical(f"{header}\n" + str().join(stack_trace)[:-1])

    @property
    def inputs(self) -> BfxWebSocketInputs:
        return self.__inputs

    def run(self) -> None:
        return asyncio.get_event_loop().run_until_complete(self.start())

    async def start(self) -> None:
        _delay = _Delay(backoff_factor=1.618)

        _sleep: Optional[Task] = None

        def _on_timeout():
            if not self.open:
                if _sleep:
                    _sleep.cancel()

        while True:
            if self.__reconnection:
                _sleep = asyncio.create_task(asyncio.sleep(int(_delay.next())))

                try:
                    await _sleep
                except asyncio.CancelledError:
                    raise ReconnectionTimeoutError(
                        "Connection has been offline for too long "
                        f"without being able to reconnect (timeout: {self.__timeout}s)."
                    ) from None

            try:
                await self.__connect()
            except (ConnectionClosedError, InvalidStatusCode, gaierror) as error:

                async def _cancel(task: Task) -> None:
                    task.cancel()

                    try:
                        await task
                    except (ConnectionClosedError, InvalidStatusCode, gaierror) as _e:
                        nonlocal error

                        if type(error) is not type(_e) or error.args != _e.args:
                            raise _e
                    except asyncio.CancelledError:
                        pass

                for bucket in self.__buckets:
                    if task := self.__buckets[bucket]:
                        self.__buckets[bucket] = None

                        await _cancel(task)

                if isinstance(error, ConnectionClosedError) and error.code in (
                    1006,
                    1012,
                ):
                    if error.code == 1006:
                        self.__logger.error("Connection lost: trying to reconnect...")

                    if error.code == 1012:
                        self.__logger.warning(
                            "WSS server is restarting: all "
                            "clients need to reconnect (server sent 20051)."
                        )

                    if self.__timeout:
                        asyncio.get_event_loop().call_later(self.__timeout, _on_timeout)

                    self.__reconnection = {
                        "attempts": 1,
                        "reason": error.reason,
                        "timestamp": datetime.now(),
                    }

                    self._authentication = False

                    _delay.reset()
                elif (
                    (isinstance(error, InvalidStatusCode) and error.status_code == 408)
                    or isinstance(error, gaierror)
                ) and self.__reconnection:
                    self.__logger.warning(
                        "Reconnection attempt unsuccessful (no."
                        f"{self.__reconnection['attempts']}): next attempt in "
                        f"~{int(_delay.peek())}.0s."
                    )

                    self.__logger.info(
                        f"The client has been offline for "
                        f"{datetime.now() - self.__reconnection['timestamp']}."
                    )

                    self.__reconnection["attempts"] += 1
                else:
                    raise error

            if not self.__reconnection:
                self.__event_emitter.emit(
                    "disconnected",
                    self._websocket.close_code,
                    self._websocket.close_reason,
                )

                break

    async def __connect(self) -> None:
        async with websockets.client.connect(self._host) as websocket:
            if self.__reconnection:
                self.__logger.warning(
                    "Reconnection attempt successful (no."
                    f"{self.__reconnection['attempts']}): recovering "
                    "connection state..."
                )

                self.__reconnection = None

            self._websocket = websocket

            for bucket in self.__buckets:
                self.__buckets[bucket] = asyncio.create_task(bucket.start())

            if len(self.__buckets) == 0 or (
                await asyncio.gather(*[bucket.wait() for bucket in self.__buckets])
            ):
                self.__event_emitter.emit("open")

            if self.__credentials:
                authentication = Connection._get_authentication_message(
                    **self.__credentials
                )

                await self._websocket.send(authentication)

            async for _message in self._websocket:
                message = json.loads(_message)

                if isinstance(message, dict):
                    if message["event"] == "info" and "version" in message:
                        if message["version"] != 2:
                            raise VersionMismatchError(
                                "Mismatch between the client and the server version: "
                                "please update bitfinex-api-py to the latest version "
                                f"to resolve this error (client version: 2, server "
                                f"version: {message['version']})."
                            )
                    elif message["event"] == "info" and message["code"] == 20051:
                        rcvd = websockets.frames.Close(
                            1012, "Stop/Restart WebSocket Server (please reconnect)."
                        )

                        raise ConnectionClosedError(rcvd=rcvd, sent=None)
                    elif message["event"] == "auth":
                        if message["status"] != "OK":
                            raise InvalidCredentialError(
                                "Can't authenticate with given API-KEY and API-SECRET."
                            )

                        self.__event_emitter.emit("authenticated", message)

                        self._authentication = True

                if (
                    isinstance(message, list)
                    and message[0] == 0
                    and message[1] != Connection._HEARTBEAT
                ):
                    self.__handler.handle(message[1], message[2])

    async def __new_bucket(self) -> BfxWebSocketBucket:
        bucket = BfxWebSocketBucket(self._host, self.__event_emitter)

        self.__buckets[bucket] = asyncio.create_task(bucket.start())

        await bucket.wait()

        return bucket

    @Connection._require_websocket_connection
    async def subscribe(
        self, channel: str, sub_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        if channel not in ["ticker", "trades", "book", "candles", "status"]:
            raise UnknownChannelError(
                "Available channels are: ticker, trades, book, candles and status."
            )

        for bucket in self.__buckets:
            if sub_id in bucket.ids:
                raise SubIdError("sub_id must be unique for all subscriptions.")

        for bucket in self.__buckets:
            if not bucket.is_full:
                return await bucket.subscribe(channel, sub_id, **kwargs)

        bucket = await self.__new_bucket()

        return await bucket.subscribe(channel, sub_id, **kwargs)

    @Connection._require_websocket_connection
    async def unsubscribe(self, sub_id: str) -> None:
        for bucket in self.__buckets:
            if bucket.has(sub_id):
                if bucket.count == 1:
                    del self.__buckets[bucket]

                    return await bucket.close(code=1001, reason="Going Away")

                return await bucket.unsubscribe(sub_id)

        raise UnknownSubscriptionError(
            f"Unable to find a subscription with sub_id <{sub_id}>."
        )

    @Connection._require_websocket_connection
    async def resubscribe(self, sub_id: str) -> None:
        for bucket in self.__buckets:
            if bucket.has(sub_id):
                return await bucket.resubscribe(sub_id)

        raise UnknownSubscriptionError(
            f"Unable to find a subscription with sub_id <{sub_id}>."
        )

    @Connection._require_websocket_connection
    async def close(self, code: int = 1000, reason: str = "") -> None:
        for bucket in self.__buckets:
            await bucket.close(code=code, reason=reason)

        if self._websocket.open:
            await self._websocket.close(code=code, reason=reason)

    @Connection._require_websocket_authentication
    async def notify(
        self, info: Any, message_id: Optional[int] = None, **kwargs: Any
    ) -> None:
        await self._websocket.send(
            json.dumps(
                [0, "n", message_id, {"type": "ucm-test", "info": info, **kwargs}]
            )
        )

    @Connection._require_websocket_authentication
    async def __handle_websocket_input(self, event: str, data: Any) -> None:
        await self._websocket.send(json.dumps([0, event, None, data], cls=JSONEncoder))

    def on(self, event, callback=None):
        return self.__event_emitter.on(event, callback)
