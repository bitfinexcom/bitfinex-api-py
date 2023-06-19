from typing import \
    TYPE_CHECKING, Optional, Dict, List, Any, cast

import asyncio, json, uuid

from websockets.legacy.client import connect as _websockets__connect

from bfxapi.websocket._connection import Connection
from bfxapi.websocket._handlers import PublicChannelsHandler
from bfxapi.websocket.exceptions import TooManySubscriptions

if TYPE_CHECKING:
    from bfxapi.websocket.subscriptions import Subscription
    from websockets.client import WebSocketClientProtocol
    from pyee import EventEmitter

class BfxWebSocketBucket(Connection):
    VERSION = 2

    MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host: str, event_emitter: "EventEmitter") -> None:
        super().__init__(host)

        self.__event_emitter = event_emitter
        self.__pendings: List[Dict[str, Any]] = [ ]
        self.__subscriptions: Dict[int, "Subscription"] = { }

        self.__condition = asyncio.locks.Condition()

        self.__handler = PublicChannelsHandler( \
            event_emitter=self.__event_emitter)

    @property
    def pendings(self) -> List[Dict[str, Any]]:
        return self.__pendings

    @property
    def subscriptions(self) -> Dict[int, "Subscription"]:
        return self.__subscriptions

    async def connect(self) -> None:
        async with _websockets__connect(self._host) as websocket:
            self._websocket = websocket

            await self.__recover_state()

            async with self.__condition:
                self.__condition.notify(1)

            async for message in self._websocket:
                message = json.loads(message)

                if isinstance(message, dict):
                    if message["event"] == "subscribed" and (chan_id := message["chanId"]):
                        self.__pendings = [ pending \
                            for pending in self.__pendings \
                                if pending["subId"] != message["subId"] ]

                        self.__subscriptions[chan_id] = cast("Subscription", message)

                        self.__event_emitter.emit("subscribed", message)
                    elif message["event"] == "unsubscribed" and (chan_id := message["chanId"]):
                        if message["status"] == "OK":
                            del self.__subscriptions[chan_id]
                    elif message["event"] == "error":
                        self.__event_emitter.emit( \
                            "wss-error", message["code"], message["msg"])

                if isinstance(message, list):
                    if (chan_id := message[0]) and message[1] != Connection.HEARTBEAT:
                        self.__handler.handle(self.__subscriptions[chan_id], message[1:])

    async def __recover_state(self) -> None:
        for pending in self.__pendings:
            await self._websocket.send( \
                json.dumps(pending))

        for _, subscription in self.__subscriptions.items():
            _subscription = cast(Dict[str, Any], subscription)

            await self.subscribe( \
                sub_id=_subscription.pop("subId"), **_subscription)

        self.__subscriptions.clear()

    @Connection.require_websocket_connection
    async def subscribe(self,
                        channel: str,
                        sub_id: Optional[str] = None,
                        **kwargs: Any) -> None:
        if len(self.__subscriptions) + len(self.__pendings) \
                == BfxWebSocketBucket.MAXIMUM_SUBSCRIPTIONS_AMOUNT:
            raise TooManySubscriptions("The client has reached the maximum number of subscriptions.")

        subscription = \
            { **kwargs, "event": "subscribe", "channel": channel }

        subscription["subId"] = sub_id or str(uuid.uuid4())

        self.__pendings.append(subscription)

        await self._websocket.send( \
            json.dumps(subscription))

    @Connection.require_websocket_connection
    async def unsubscribe(self, sub_id: str) -> None:
        for subscription in self.__subscriptions.values():
            if subscription["subId"] == sub_id:
                data = { "event": "unsubscribe", \
                    "chanId": subscription["subId"] }

                message = json.dumps(data)

                await self._websocket.send(message)

    @Connection.require_websocket_connection
    async def close(self, code: int = 1000, reason: str = str()) -> None:
        await self._websocket.close(code=code, reason=reason)

    def has(self, sub_id: str) -> bool:
        for subscription in self.__subscriptions.values():
            if subscription["subId"] == sub_id:
                return True

        return False

    async def wait(self) -> None:
        async with self.__condition:
            await self.__condition.wait_for(
                lambda: self.open)
