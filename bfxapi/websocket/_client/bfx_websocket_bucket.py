from typing import \
    List, Dict, Any, \
    Optional, cast

import asyncio, json, uuid

import websockets.client

from pyee import EventEmitter
from bfxapi.websocket._connection import Connection
from bfxapi.websocket._handlers import PublicChannelsHandler
from bfxapi.websocket.subscriptions import Subscription

from bfxapi.websocket.exceptions import FullBucketError

_CHECKSUM_FLAG_VALUE = 131_072

def _strip(message: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return { key: message[key] for key in message if not key in keys }

class BfxWebSocketBucket(Connection):
    __MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host: str, event_emitter: EventEmitter) -> None:
        super().__init__(host)

        self.__event_emitter = event_emitter
        self.__pendings: List[Dict[str, Any]] = [ ]
        self.__subscriptions: Dict[int, Subscription] = { }

        self.__condition = asyncio.locks.Condition()

        self.__handler = PublicChannelsHandler( \
            event_emitter=self.__event_emitter)

    @property
    def count(self) -> int:
        return len(self.__pendings) + \
            len(self.__subscriptions)

    @property
    def is_full(self) -> bool:
        return self.count == \
            BfxWebSocketBucket.__MAXIMUM_SUBSCRIPTIONS_AMOUNT

    async def start(self) -> None:
        async with websockets.client.connect(self._host) as websocket:
            self._websocket = websocket

            await self.__recover_state()

            async with self.__condition:
                self.__condition.notify(1)

            async for _message in self._websocket:
                message = json.loads(_message)

                if isinstance(message, dict):
                    # I think there's a better way to do it...
                    if "chanId" in message:
                        message["chan_id"] = message.pop("chanId")

                    if "subId" in message:
                        message["sub_id"] = message.pop("subId")

                    if message["event"] == "subscribed":
                        self.__on_subscribed(message)
                    elif message["event"] == "unsubscribed":
                        if message["status"] == "OK":
                            chan_id = cast(int, message["chan_id"])

                            del self.__subscriptions[chan_id]
                    elif message["event"] == "error":
                        self.__event_emitter.emit("wss-error", \
                            message["code"], message["msg"])

                if isinstance(message, list):
                    if (chan_id := cast(int, message[0])) and \
                            (message[1] != Connection._HEARTBEAT):
                        self.__handler.handle(self.__subscriptions[chan_id], message[1:])

    def __on_subscribed(self, message: Dict[str, Any]) -> None:
        chan_id = cast(int, message["chan_id"])

        subscription = cast(Subscription, _strip(message, \
            keys=["event", "chan_id", "pair", "currency"]))

        self.__pendings = [ pending \
            for pending in self.__pendings \
                if pending["subId"] != message["sub_id"] ]

        self.__subscriptions[chan_id] = subscription

        self.__event_emitter.emit("subscribed", subscription)

    async def __recover_state(self) -> None:
        for pending in self.__pendings:
            await self._websocket.send(message = \
                json.dumps(pending))

        for chan_id in list(self.__subscriptions.keys()):
            subscription = self.__subscriptions.pop(chan_id)

            await self.subscribe(**subscription)

        await self.__set_config([ _CHECKSUM_FLAG_VALUE ])

    async def __set_config(self, flags: List[int]) -> None:
        await self._websocket.send(json.dumps( \
            { "event": "conf", "flags": sum(flags) }))

    @Connection.require_websocket_connection
    async def subscribe(self,
                        channel: str,
                        sub_id: Optional[str] = None,
                        **kwargs: Any) -> None:
        if self.is_full:
            raise FullBucketError("The bucket is full: " + \
                "can't subscribe to any other channel.")

        subscription: Dict[str, Any] = \
            { **kwargs, "event": "subscribe", "channel": channel }

        subscription["subId"] = sub_id or str(uuid.uuid4())

        self.__pendings.append(subscription)

        await self._websocket.send(message = \
            json.dumps(subscription))

    @Connection.require_websocket_connection
    async def unsubscribe(self, sub_id: str) -> None:
        for chan_id, subscription in self.__subscriptions.items():
            if subscription["sub_id"] == sub_id:
                unsubscription = {
                    "event": "unsubscribe",
                        "chanId": chan_id }

                await self._websocket.send(message = \
                    json.dumps(unsubscription))

    @Connection.require_websocket_connection
    async def resubscribe(self, sub_id: str) -> None:
        for subscription in self.__subscriptions.values():
            if subscription["sub_id"] == sub_id:
                await self.unsubscribe(sub_id)

                await self.subscribe(**subscription)

    @Connection.require_websocket_connection
    async def close(self, code: int = 1000, reason: str = str()) -> None:
        await self._websocket.close(code, reason)

    def has(self, sub_id: str) -> bool:
        for subscription in self.__subscriptions.values():
            if subscription["sub_id"] == sub_id:
                return True

        return False

    async def wait(self) -> None:
        async with self.__condition:
            await self.__condition \
                .wait_for(lambda: self.open)
