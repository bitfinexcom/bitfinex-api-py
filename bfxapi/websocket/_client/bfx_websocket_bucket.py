import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Set, cast

import websockets.client
from pyee import EventEmitter

from bfxapi._utils.json_decoder import JSONDecoder
from bfxapi.websocket._connection import Connection
from bfxapi.websocket._handlers import PublicChannelsHandler
from bfxapi.websocket.subscriptions import Subscription

_CHECKSUM_FLAG_VALUE = 131_072


def _strip(message: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return {key: value for key, value in message.items() if key not in keys}


class BfxWebSocketBucket(Connection):
    __MAXIMUM_SUBSCRIPTIONS_AMOUNT = 25

    def __init__(self, host: str, event_emitter: EventEmitter) -> None:
        super().__init__(host)

        self.__event_emitter = event_emitter
        self.__pendings: List[Dict[str, Any]] = []
        self.__subscriptions: Dict[int, Subscription] = {}
        self.__cancellations: Set[str] = set()

        self.__condition = asyncio.locks.Condition()

        self.__handler = PublicChannelsHandler(event_emitter=self.__event_emitter)

    @property
    def count(self) -> int:
        return len(self.__pendings) + len(self.__subscriptions)

    @property
    def is_full(self) -> bool:
        return self.count == BfxWebSocketBucket.__MAXIMUM_SUBSCRIPTIONS_AMOUNT

    @property
    def ids(self) -> List[str]:
        return [pending["subId"] for pending in self.__pendings] + [
            subscription["sub_id"] for subscription in self.__subscriptions.values()
        ]

    async def start(self) -> None:
        async with websockets.client.connect(self._host) as websocket:
            self._websocket = websocket

            await self.__recover_state()

            async with self.__condition:
                self.__condition.notify(1)

            async for _message in self._websocket:
                message = json.loads(_message, cls=JSONDecoder)

                if isinstance(message, dict):
                    if message["event"] == "subscribed":
                        await self.__on_subscribed(message)

                if isinstance(message, list):
                    if (
                        (chan_id := cast(int, message[0]))
                        and (subscription := self.__subscriptions.get(chan_id))
                        and (message[1] != Connection._HEARTBEAT)
                    ):
                        self.__handler.handle(subscription, message[1:])

    async def __on_subscribed(self, message: Dict[str, Any]) -> None:
        chan_id = cast(int, message["chan_id"])

        sub_id = cast(str, message["sub_id"])

        self.__pendings = [
            pending for pending in self.__pendings if pending["subId"] != sub_id
        ]

        if sub_id in self.__cancellations:
            # Unsubscribed while still pending. The subscribe frame was
            # already on the wire, so the server opened the channel anyway -
            # and this confirmation is the first moment a chan_id exists to
            # close it with. Without this the channel streams forever into a
            # consumer that believes it cancelled the subscription.
            self.__cancellations.discard(sub_id)

            await self._websocket.send(
                message=json.dumps({"event": "unsubscribe", "chanId": chan_id})
            )

            return

        subscription = cast(
            Subscription, _strip(message, keys=["chan_id", "event", "pair", "currency"])
        )

        self.__subscriptions[chan_id] = subscription

        self.__event_emitter.emit("subscribed", subscription)

    async def __recover_state(self) -> None:
        # A cancellation waits for a confirmation that can only arrive on the
        # socket that has just gone; the pending it referred to was dropped
        # when it was recorded, so nothing re-requests it either.
        self.__cancellations.clear()

        for pending in self.__pendings:
            await self._websocket.send(message=json.dumps(pending))

        for chan_id in list(self.__subscriptions.keys()):
            subscription = self.__subscriptions.pop(chan_id)

            await self.subscribe(**subscription)

        await self.__set_config([_CHECKSUM_FLAG_VALUE])

    async def __set_config(self, flags: List[int]) -> None:
        await self._websocket.send(json.dumps({"event": "conf", "flags": sum(flags)}))

    @Connection._require_websocket_connection
    async def subscribe(
        self, channel: str, sub_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        subscription: Dict[str, Any] = {
            **kwargs,
            "event": "subscribe",
            "channel": channel,
        }

        subscription["subId"] = sub_id or str(uuid.uuid4())

        self.__pendings.append(subscription)

        await self._websocket.send(message=json.dumps(subscription))

    @Connection._require_websocket_connection
    async def unsubscribe(self, sub_id: str) -> None:
        for pending in self.__pendings:
            if pending["subId"] == sub_id:
                # No chan_id exists yet, so there is nothing to unsubscribe
                # from: drop the request here and close the channel the moment
                # the server confirms it (see __on_subscribed).
                self.__pendings.remove(pending)

                self.__cancellations.add(sub_id)

                return

        for chan_id, subscription in list(self.__subscriptions.items()):
            if subscription["sub_id"] == sub_id:
                unsubscription = {"event": "unsubscribe", "chanId": chan_id}

                del self.__subscriptions[chan_id]

                await self._websocket.send(message=json.dumps(unsubscription))

    @Connection._require_websocket_connection
    async def resubscribe(self, sub_id: str) -> None:
        # Only confirmed subscriptions are reissued. A pending one is already
        # being established and its frame has not been answered yet: sending
        # it again would open two channels under a single sub_id.
        for subscription in list(self.__subscriptions.values()):
            if subscription["sub_id"] == sub_id:
                await self.unsubscribe(sub_id)

                await self.subscribe(**subscription)

    @Connection._require_websocket_connection
    async def close(self, code: int = 1000, reason: str = "") -> None:
        await self._websocket.close(code, reason)

    def has(self, sub_id: str) -> bool:
        # `ids` counts pendings, so a duplicate `subscribe` is refused from the
        # instant the frame is sent. `has` counted only confirmed ones, which
        # left a sub_id that was simultaneously "taken" (SubIdError) and
        # "unknown" (UnknownSubscriptionError) - unusable and uncancellable.
        # The window is not a few milliseconds either: __recover_state moves
        # EVERY subscription back to pending, so after each reconnection the
        # whole set is unreachable until the server has confirmed it.
        if any(pending["subId"] == sub_id for pending in self.__pendings):
            return True

        return any(
            subscription["sub_id"] == sub_id
            for subscription in self.__subscriptions.values()
        )

    async def wait(self) -> None:
        async with self.__condition:
            await self.__condition.wait_for(lambda: self.open)
