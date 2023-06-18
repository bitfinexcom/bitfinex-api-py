from typing import \
    TYPE_CHECKING, List, Dict, Any

from collections import defaultdict

from pyee.asyncio import AsyncIOEventEmitter

if TYPE_CHECKING:
    from bfxapi.websocket.subscriptions import Subscription

class BfxEventEmitter(AsyncIOEventEmitter):
    def __init__(self, targets: List[str]) -> None:
        super().__init__()

        self.__targets = targets

        self.__log: Dict[str, List[str]] = \
            defaultdict(lambda: [ ])

    def emit(self,
             event: str,
             *args: Any,
             **kwargs: Any) -> bool:
        if event in self.__targets:
            subscription: "Subscription" = args[0]

            sub_id = subscription["subId"]

            if event in self.__log[sub_id]:
                with self._lock:
                    listeners = self._events.get(event)

                return bool(listeners)

            self.__log[sub_id] += [ event ]

        return super().emit(event, *args, **kwargs)
