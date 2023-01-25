from decimal import Decimal
from datetime import datetime

from typing import Union, Optional, List, Tuple
from .types import JSON
from .enums import OrderType, FundingOfferType

def _strip(dictionary):
    return { key: value for key, value in dictionary.items() if value != None}

class _BfxWebsocketInputs(object):
    def __init__(self, __handle_websocket_input):
        self.__handle_websocket_input = __handle_websocket_input

    async def submit_order(self, type: OrderType, symbol: str, amount: Union[Decimal, float, str], 
                     price: Optional[Union[Decimal, float, str]] = None, lev: Optional[int] = None, 
                     price_trailing: Optional[Union[Decimal, float, str]] = None, price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_oco_stop: Optional[Union[Decimal, float, str]] = None,
                     gid: Optional[int] = None, cid: Optional[int] = None,
                     flags: Optional[int] = 0, tif: Optional[Union[datetime, str]] = None, meta: Optional[JSON] = None):
        data = _strip({
            "type": type, "symbol": symbol, "amount": amount,
            "price": price, "lev": lev,
            "price_trailing": price_trailing, "price_aux_limit": price_aux_limit, "price_oco_stop": price_oco_stop,
            "gid": gid, "cid": cid,
            "flags": flags, "tif": tif, "meta": meta
        })
        
        await self.__handle_websocket_input("on", data)

    async def update_order(self, id: int, amount: Optional[Union[Decimal, float, str]] = None, price: Optional[Union[Decimal, float, str]] = None,
                     cid: Optional[int] = None, cid_date: Optional[str] = None, gid: Optional[int] = None,
                     flags: Optional[int] = 0, lev: Optional[int] = None, delta: Optional[Union[Decimal, float, str]] = None,
                     price_aux_limit: Optional[Union[Decimal, float, str]] = None, price_trailing: Optional[Union[Decimal, float, str]] = None, tif: Optional[Union[datetime, str]] = None):
        data = _strip({
            "id": id, "amount": amount, "price": price,
            "cid": cid, "cid_date": cid_date, "gid": gid,
            "flags": flags, "lev": lev, "delta": delta,
            "price_aux_limit": price_aux_limit, "price_trailing": price_trailing, "tif": tif
        })
        
        await self.__handle_websocket_input("ou", data)

    async def cancel_order(self, id: Optional[int] = None, cid: Optional[int] = None, cid_date: Optional[str] = None):
        data = _strip({ 
            "id": id, 
            "cid": cid, 
            "cid_date": cid_date 
        })

        await self.__handle_websocket_input("oc", data)

    async def cancel_order_multi(self, ids: Optional[List[int]] = None, cids: Optional[List[Tuple[int, str]]] = None, gids: Optional[List[int]] = None, all: bool = False):
        data = _strip({
            "ids": ids,
            "cids": cids,
            "gids": gids,

            "all": int(all)
        })
        
        await self.__handle_websocket_input("oc_multi", data)

    async def submit_funding_offer(self, type: FundingOfferType, symbol: str, amount: Union[Decimal, float, str],
                             rate: Union[Decimal, float, str], period: int,
                             flags: Optional[int] = 0):
        data = {
            "type": type, "symbol": symbol, "amount": amount,
            "rate": rate, "period": period, 
            "flags": flags
        }

        await self.__handle_websocket_input("fon", data)

    async def cancel_funding_offer(self, id: int):
        await self.__handle_websocket_input("foc", { "id": id })

    async def calc(self, *args: str):
        await self.__handle_websocket_input("calc", list(map(lambda arg: [arg], args)))