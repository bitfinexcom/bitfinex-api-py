from typing import Type, List, Dict, TypedDict, Union, Optional, Any

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]

BalanceUpdateStream = TypedDict("BalanceUpdateStream", {
    "AUM": float,
    "AUM_NET": float
})

WalletSnapshotStream = List[TypedDict("WalletSnapshotStream", {
    "WALLET_TYPE": str,
    "CURRENCY": str,
    "BALANCE": float,
    "UNSETTLED_INTEREST": float,
    "BALANCE_AVAILABLE": Optional[float],
    "DESCRIPTION": str,
    "META": JSON
})]

WalletUpdateStream = TypedDict("WalletUpdateStream", {
    "WALLET_TYPE": str,
    "CURRENCY": str,
    "BALANCE": float,
    "UNSETTLED_INTEREST": float,
    "BALANCE_AVAILABLE": Optional[float],
    "DESCRIPTION": str,
    "META": JSON
})

OrderSnapshotStream = List[TypedDict("OrderSnapshotStream", {
    "ID": int, 
    "GID": int, 
    "CID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int, 
    "MTS_UPDATE": int, 
    "AMOUNT": float, 
    "AMOUNT_ORIG": float, 
    "ORDER_TYPE": str, 
    "TYPE_PREV": str, 
    "MTS_TIF": int, 
    "FLAGS": int, 
    "STATUS": str, 
    "PRICE": float, 
    "PRICE_AVG": float,
    "PRICE_TRAILING": float, 
    "PRICE_AUX_LIMIT": float, 
    "NOTIFY": int,
    "HIDDEN": int, 
    "PLACED_ID": int, 
    "ROUTING": str, 
    "META": JSON
})]

NewOrderStream = TypedDict("NewOrderStream", {
    "ID": int, 
    "GID": int, 
    "CID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int, 
    "MTS_UPDATE": int, 
    "AMOUNT": float, 
    "AMOUNT_ORIG": float, 
    "ORDER_TYPE": str, 
    "TYPE_PREV": str, 
    "MTS_TIF": int, 
    "FLAGS": int, 
    "ORDER_STATUS": str, 
    "PRICE": float, 
    "PRICE_AVG": float,
    "PRICE_TRAILING": float, 
    "PRICE_AUX_LIMIT": float, 
    "NOTIFY": int,
    "HIDDEN": int, 
    "PLACED_ID": int, 
    "ROUTING": str
})

OrderUpdateStream = TypedDict("OrderUpdateStream", {
    "ID": int, 
    "GID": int, 
    "CID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int, 
    "MTS_UPDATE": int, 
    "AMOUNT": float, 
    "AMOUNT_ORIG": float, 
    "ORDER_TYPE": str, 
    "TYPE_PREV": str, 
    "MTS_TIF": int, 
    "FLAGS": int, 
    "ORDER_STATUS": str, 
    "PRICE": float, 
    "PRICE_AVG": float,
    "PRICE_TRAILING": float, 
    "PRICE_AUX_LIMIT": float, 
    "NOTIFY": int,
    "HIDDEN": int, 
    "PLACED_ID": int, 
    "ROUTING": str
})

OrderCancelStream = TypedDict("OrderCancelStream", {
    "ID": int, 
    "GID": int, 
    "CID": int, 
    "SYMBOL": str, 
    "MTS_CREATE": int, 
    "MTS_UPDATE": int, 
    "AMOUNT": float, 
    "AMOUNT_ORIG": float, 
    "ORDER_TYPE": str, 
    "TYPE_PREV": str, 
    "MTS_TIF": int, 
    "FLAGS": int, 
    "ORDER_STATUS": str, 
    "PRICE": float, 
    "PRICE_AVG": float,
    "PRICE_TRAILING": float, 
    "PRICE_AUX_LIMIT": float, 
    "NOTIFY": int,
    "HIDDEN": int, 
    "PLACED_ID": int, 
    "ROUTING": str
})