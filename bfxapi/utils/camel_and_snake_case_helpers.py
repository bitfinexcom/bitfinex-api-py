import re

from typing import TypeVar, Callable, cast

T = TypeVar("T")

_to_snake_case: Callable[[str], str] = lambda string: re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()

_to_camel_case: Callable[[str], str] = lambda string: \
    (components := string.split("_"))[0] + str().join(c.title() for c in components[1:])

def _scheme(data: T, adapter: Callable[[str], str]) -> T:
    if isinstance(data, list):
        return cast(T, [ _scheme(sub_data, adapter) for sub_data in data ])
    if isinstance(data, dict):
        return cast(T, { adapter(key): _scheme(value, adapter) for key, value in data.items() })
    return data

def to_snake_case_keys(dictionary: T) -> T:
    return _scheme(dictionary, _to_snake_case)

def to_camel_case_keys(dictionary: T) -> T:
    return _scheme(dictionary, _to_camel_case)
