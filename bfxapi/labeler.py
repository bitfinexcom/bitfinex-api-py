from .exceptions import LabelerSerializerException

from typing import Generic, TypeVar, Iterable, Optional, List, Tuple, Any, cast

from types import SimpleNamespace

T = TypeVar("T")

class _Serializer(Generic[T]):
    def __init__(self, name: str, labels: List[str], IGNORE: List[str] = [ "_PLACEHOLDER" ]):
        self.name, self.__labels, self.__IGNORE = name, labels, IGNORE

    def _serialize(self, *args: Any, skip: Optional[List[str]] = None) -> Iterable[Tuple[str, Any]]:
        labels = list(filter(lambda label: label not in (skip or list()), self.__labels))

        if len(labels) > len(args):
            raise LabelerSerializerException("<labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(labels):
            if label not in self.__IGNORE:
                yield label, args[index]

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> T:
        return cast(T, SimpleNamespace(**dict(self._serialize(*values, skip=skip))))