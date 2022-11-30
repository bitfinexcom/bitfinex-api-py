from typing import Generic, TypeVar, Iterable, List, Any

from . import typings

from .exceptions import BfxRestException

T = TypeVar("T")

class _Serializer(Generic[T]):
    def __init__(self, name: str, labels: List[str]):
        self.name, self.__labels = name, labels

    def __serialize(self, *args: Any, IGNORE: List[str] = [ "_PLACEHOLDER" ]) -> Iterable[T]:
        if len(self.__labels) != len(args):
            raise BfxRestException("<self.__labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(self.__labels):
            if label not in IGNORE:
                yield label, args[index]

    def parse(self, *values: Any) -> T:
        return dict(self.__serialize(*values))

#region Serializers definition for Rest Public Endpoints

PlatformStatus = _Serializer[typings.PlatformStatus]("PlatformStatus", labels=[
    "OPERATIVE"
])

#endregion