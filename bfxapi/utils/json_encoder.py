import json
from decimal import Decimal
from datetime import datetime

from typing import Type, List, Dict, Union, Any

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

def _strip(dictionary: Dict) -> Dict:
    return { key: value for key, value in dictionary.items() if value is not None }

def _convert_float_to_str(data: JSON) -> JSON:
    if isinstance(data, float):
        return format(Decimal(repr(data)), "f")
    if isinstance(data, list):
        return [ _convert_float_to_str(sub_data) for sub_data in data ]
    if isinstance(data, dict):
        return _strip({ key: _convert_float_to_str(value) for key, value in data.items() })
    return data

class JSONEncoder(json.JSONEncoder):
    def encode(self, o: JSON) -> str:
        return json.JSONEncoder.encode(self, _convert_float_to_str(o))

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return format(o, "f")
        if isinstance(o, datetime):
            return str(o)

        return json.JSONEncoder.default(self, o)
