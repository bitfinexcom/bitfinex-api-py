import json
from decimal import Decimal
from datetime import datetime

from typing import Type, List, Dict, Union, Any

JSON = Union[Dict[str, "JSON"], List["JSON"], bool, int, float, str, Type[None]]

def _strip(dictionary: Dict) -> Dict:
    return { key: value for key, value in dictionary.items() if value != None}

def _convert_float_to_str(data: JSON) -> JSON:
    if isinstance(data, float):
        return format(Decimal(repr(data)), "f")
    elif isinstance(data, list):
        return [ _convert_float_to_str(sub_data) for sub_data in data ]
    elif isinstance(data, dict):
        return _strip({ key: _convert_float_to_str(value) for key, value in data.items() })
    else: return data

class JSONEncoder(json.JSONEncoder):
    def encode(self, obj: JSON) -> str:
        return json.JSONEncoder.encode(self, _convert_float_to_str(obj))

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal): return format(obj, "f")
        elif isinstance(obj, datetime): return str(obj)

        return json.JSONEncoder.default(self, obj)