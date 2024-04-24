from asyncio import AbstractEventLoop
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from pyee.asyncio import AsyncIOEventEmitter

from bfxapi.websocket.exceptions import UnknownEventError

_Handler = TypeVar("_Handler", bound=Callable[..., None])

_ONCE_PER_CONNECTION = [
    "open",
    "authenticated",
    "order_snapshot",
    "position_snapshot",
    "funding_offer_snapshot",
    "funding_credit_snapshot",
    "funding_loan_snapshot",
    "wallet_snapshot",
]

_ONCE_PER_SUBSCRIPTION = [
    "subscribed",
    "t_trades_snapshot",
    "f_trades_snapshot",
    "t_book_snapshot",
    "f_book_snapshot",
    "t_raw_book_snapshot",
    "f_raw_book_snapshot",
    "candles_snapshot",
]

_COMMON = [
    "disconnected",
    "t_ticker_update",
    "f_ticker_update",
    "t_trade_execution",
    "t_trade_execution_update",
    "f_trade_execution",
    "f_trade_execution_update",
    "t_book_update",
    "f_book_update",
    "t_raw_book_update",
    "f_raw_book_update",
    "candles_update",
    "derivatives_status_update",
    "liquidation_feed_update",
    "checksum",
    "order_new",
    "order_update",
    "order_cancel",
    "position_new",
    "position_update",
    "position_close",
    "funding_offer_new",
    "funding_offer_update",
    "funding_offer_cancel",
    "funding_credit_new",
    "funding_credit_update",
    "funding_credit_close",
    "funding_loan_new",
    "funding_loan_update",
    "funding_loan_close",
    "trade_execution",
    "trade_execution_update",
    "wallet_update",
    "base_margin_info",
    "symbol_margin_info",
    "funding_info_update",
    "balance_update",
    "notification",
    "on-req-notification",
    "ou-req-notification",
    "oc-req-notification",
    "fon-req-notification",
    "foc-req-notification",
]


class BfxEventEmitter(AsyncIOEventEmitter):
    _EVENTS = _ONCE_PER_CONNECTION + _ONCE_PER_SUBSCRIPTION + _COMMON

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
        super().__init__(loop)

        self._connection: List[str] = []

        self._subscriptions: Dict[str, List[str]] = defaultdict(lambda: [])

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        if event in _ONCE_PER_CONNECTION:
            if event in self._connection:
                return self._has_listeners(event)

            self._connection += [event]

        if event in _ONCE_PER_SUBSCRIPTION:
            sub_id = args[0]["sub_id"]

            if event in self._subscriptions[sub_id]:
                return self._has_listeners(event)

            self._subscriptions[sub_id] += [event]

        return super().emit(event, *args, **kwargs)

    def on(
        self, event: str, f: Optional[_Handler] = None
    ) -> Union[_Handler, Callable[[_Handler], _Handler]]:
        if event not in BfxEventEmitter._EVENTS:
            raise UnknownEventError(
                f"Can't register to unknown event: <{event}> (to get a full "
                "list of available events see https://docs.bitfinex.com/)."
            )

        return super().on(event, f)

    def _has_listeners(self, event: str) -> bool:
        with self._lock:
            listeners = self._events.get(event)

        return bool(listeners)
