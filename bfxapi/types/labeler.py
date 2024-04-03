from typing import Any, Dict, Generic, Iterable, List, Tuple, Type, TypeVar, cast

T = TypeVar("T", bound="_Type")


def compose(*decorators):
    def wrapper(function):
        for decorator in reversed(decorators):
            function = decorator(function)
        return function

    return wrapper


def partial(cls):
    def __init__(self, **kwargs):
        for annotation in self.__annotations__.keys():
            if annotation not in kwargs:
                self.__setattr__(annotation, None)
            else:
                self.__setattr__(annotation, kwargs[annotation])

            kwargs.pop(annotation, None)

        if len(kwargs) != 0:
            raise TypeError(
                f"{cls.__name__}.__init__() got an unexpected keyword argument "
                f"'{list(kwargs.keys())[0]}'"
            )

    cls.__init__ = __init__

    return cls


class _Type:
    """
    Base class for any dataclass serializable by the _Serializer generic class.
    """


class _Serializer(Generic[T]):
    def __init__(
        self, name: str, klass: Type[_Type], labels: List[str], *, flat: bool = False
    ):
        self.name, self.klass, self.__labels, self.__flat = name, klass, labels, flat

    def _serialize(self, *args: Any) -> Iterable[Tuple[str, Any]]:
        if self.__flat:
            args = tuple(_Serializer.__flatten(list(args)))

        if len(self.__labels) > len(args):
            raise AssertionError(
                f"{self.name} -> <labels> and <*args> "
                "arguments should contain the same amount of elements."
            )

        for index, label in enumerate(self.__labels):
            if label != "_PLACEHOLDER":
                yield label, args[index]

    def parse(self, *values: Any) -> T:
        return cast(T, self.klass(**dict(self._serialize(*values))))

    def get_labels(self) -> List[str]:
        return [label for label in self.__labels if label != "_PLACEHOLDER"]

    @classmethod
    def __flatten(cls, array: List[Any]) -> List[Any]:
        if len(array) == 0:
            return array

        if isinstance(array[0], list):
            return cls.__flatten(array[0]) + cls.__flatten(array[1:])

        return array[:1] + cls.__flatten(array[1:])


class _RecursiveSerializer(_Serializer, Generic[T]):
    def __init__(
        self,
        name: str,
        klass: Type[_Type],
        labels: List[str],
        *,
        serializers: Dict[str, _Serializer[Any]],
        flat: bool = False,
    ):
        super().__init__(name, klass, labels, flat=flat)

        self.serializers = serializers

    def parse(self, *values: Any) -> T:
        serialization = dict(self._serialize(*values))

        for key in serialization:
            if key in self.serializers.keys():
                serialization[key] = self.serializers[key].parse(*serialization[key])

        return cast(T, self.klass(**serialization))


def generate_labeler_serializer(
    name: str, klass: Type[T], labels: List[str], *, flat: bool = False
) -> _Serializer[T]:
    return _Serializer[T](name, klass, labels, flat=flat)


def generate_recursive_serializer(
    name: str,
    klass: Type[T],
    labels: List[str],
    *,
    serializers: Dict[str, _Serializer[Any]],
    flat: bool = False,
) -> _RecursiveSerializer[T]:
    return _RecursiveSerializer[T](
        name, klass, labels, serializers=serializers, flat=flat
    )
