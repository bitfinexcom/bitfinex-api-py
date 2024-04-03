from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

_Handler = Callable[[str, Any], Awaitable[None]]


class BfxWebSocketInputs:
    def __init__(self, handle_websocket_input: _Handler) -> None:
        self.__handle_websocket_input = handle_websocket_input

    async def submit_order(
        self,
        type: str,
        symbol: str,
        amount: Union[str, float, Decimal],
        price: Union[str, float, Decimal],
        *,
        lev: Optional[int] = None,
        price_trailing: Optional[Union[str, float, Decimal]] = None,
        price_aux_limit: Optional[Union[str, float, Decimal]] = None,
        price_oco_stop: Optional[Union[str, float, Decimal]] = None,
        gid: Optional[int] = None,
        cid: Optional[int] = None,
        flags: Optional[int] = None,
        tif: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "on",
            {
                "type": type,
                "symbol": symbol,
                "amount": amount,
                "price": price,
                "lev": lev,
                "price_trailing": price_trailing,
                "price_aux_limit": price_aux_limit,
                "price_oco_stop": price_oco_stop,
                "gid": gid,
                "cid": cid,
                "flags": flags,
                "tif": tif,
                "meta": meta,
            },
        )

    async def update_order(
        self,
        id: int,
        *,
        amount: Optional[Union[str, float, Decimal]] = None,
        price: Optional[Union[str, float, Decimal]] = None,
        cid: Optional[int] = None,
        cid_date: Optional[str] = None,
        gid: Optional[int] = None,
        flags: Optional[int] = None,
        lev: Optional[int] = None,
        delta: Optional[Union[str, float, Decimal]] = None,
        price_aux_limit: Optional[Union[str, float, Decimal]] = None,
        price_trailing: Optional[Union[str, float, Decimal]] = None,
        tif: Optional[str] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "ou",
            {
                "id": id,
                "amount": amount,
                "price": price,
                "cid": cid,
                "cid_date": cid_date,
                "gid": gid,
                "flags": flags,
                "lev": lev,
                "delta": delta,
                "price_aux_limit": price_aux_limit,
                "price_trailing": price_trailing,
                "tif": tif,
            },
        )

    async def cancel_order(
        self,
        *,
        id: Optional[int] = None,
        cid: Optional[int] = None,
        cid_date: Optional[str] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "oc", {"id": id, "cid": cid, "cid_date": cid_date}
        )

    async def cancel_order_multi(
        self,
        *,
        id: Optional[List[int]] = None,
        cid: Optional[List[Tuple[int, str]]] = None,
        gid: Optional[List[int]] = None,
        all: Optional[bool] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "oc_multi", {"id": id, "cid": cid, "gid": gid, "all": all}
        )

    async def submit_funding_offer(
        self,
        type: str,
        symbol: str,
        amount: Union[str, float, Decimal],
        rate: Union[str, float, Decimal],
        period: int,
        *,
        flags: Optional[int] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "fon",
            {
                "type": type,
                "symbol": symbol,
                "amount": amount,
                "rate": rate,
                "period": period,
                "flags": flags,
            },
        )

    async def cancel_funding_offer(self, id: int) -> None:
        await self.__handle_websocket_input("foc", {"id": id})

    async def calc(self, *args: str) -> None:
        await self.__handle_websocket_input("calc", list(map(lambda arg: [arg], args)))
