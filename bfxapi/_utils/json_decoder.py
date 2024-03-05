import json
import re
from typing import Any, Dict


def _to_snake_case(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def _object_hook(data: Dict[str, Any]) -> Any:
    return {_to_snake_case(key): value for key, value in data.items()}


class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, object_hook=_object_hook)
