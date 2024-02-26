import json
from decimal import Decimal
from typing import Any, Dict, List, Union

_ExtJSON = Union[
    Dict[str, "_ExtJSON"], List["_ExtJSON"], bool, int, float, str, Decimal, None
]

_StrictJSON = Union[Dict[str, "_StrictJSON"], List["_StrictJSON"], int, str, None]


def _clear(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in dictionary.items() if value is not None}


def _adapter(data: _ExtJSON) -> _StrictJSON:
    if isinstance(data, bool):
        return int(data)
    if isinstance(data, float):
        return format(Decimal(repr(data)), "f")
    if isinstance(data, Decimal):
        return format(data, "f")

    if isinstance(data, list):
        return [_adapter(sub_data) for sub_data in data]
    if isinstance(data, dict):
        return _clear({key: _adapter(value) for key, value in data.items()})

    return data


class JSONEncoder(json.JSONEncoder):
    def encode(self, o: _ExtJSON) -> str:
        return super().encode(_adapter(o))
