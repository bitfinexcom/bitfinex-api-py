from .exceptions import LabelerSerializerException

from typing import Type, Generic, TypeVar, Iterable, Optional, List, Tuple, Any, cast

T = TypeVar("T", bound="_Type")

class _Type(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

class _Serializer(Generic[T]):
    def __init__(self, name: str, klass: Type[_Type], labels: List[str], IGNORE: List[str] = [ "_PLACEHOLDER" ]):
        self.name, self.klass, self.__labels, self.__IGNORE = name, klass, labels, IGNORE

    def _serialize(self, *args: Any, skip: Optional[List[str]] = None) -> Iterable[Tuple[str, Any]]:
        labels = list(filter(lambda label: label not in (skip or list()), self.__labels))

        if len(labels) > len(args):
            raise LabelerSerializerException("<labels> and <*args> arguments should contain the same amount of elements.")

        for index, label in enumerate(labels):
            if label not in self.__IGNORE:
                yield label, args[index]

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> T:
        return cast(T, self.klass(**dict(self._serialize(*values, skip=skip))))

def generate_labeler_serializer(name: str, klass: Type[T], labels: List[str], IGNORE: List[str] = [ "_PLACEHOLDER" ]) -> _Serializer[T]:
    return _Serializer[T](name, klass, labels, IGNORE)