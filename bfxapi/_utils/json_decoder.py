from typing import Dict, Any

import re, json

def _to_snake_case(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()

def _object_hook(data: Dict[str, Any]) -> Any:
    return { _to_snake_case(key): value for key, value in data.items() }

class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(object_hook=_object_hook, *args, **kwargs)
