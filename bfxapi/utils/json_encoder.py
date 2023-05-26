import json

from decimal import Decimal

from typing import List, Dict, Union

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, None]

_CustomJSON = Union[Dict[str, "_CustomJSON"], List["_CustomJSON"], \
    bool, int, float, str, Decimal, None]

def _strip(dictionary: Dict) -> Dict:
    return { key: value for key, value in dictionary.items() if value is not None }

def _convert_data_to_json(data: _CustomJSON) -> JSON:
    if isinstance(data, bool):
        return int(data)
    if isinstance(data, float):
        return format(Decimal(repr(data)), "f")
    if isinstance(data, Decimal):
        return format(data, "f")

    if isinstance(data, list):
        return [ _convert_data_to_json(sub_data) for sub_data in data ]
    if isinstance(data, dict):
        return _strip({ key: _convert_data_to_json(value) for key, value in data.items() })

    return data

class JSONEncoder(json.JSONEncoder):
    def encode(self, o: _CustomJSON) -> str:
        return json.JSONEncoder.encode(self, _convert_data_to_json(o))
