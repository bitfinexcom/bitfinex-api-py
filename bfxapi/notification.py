from typing import List, Dict, Union, Optional, Any, TypedDict, Generic, TypeVar, cast
from dataclasses import dataclass
from .labeler import _Type, _Serializer

T = TypeVar("T")

@dataclass
class Notification(_Type, Generic[T]):
    mts: int
    type: str 
    message_id: Optional[int]
    data: T
    code: Optional[int]
    status: str
    text: str

class _Notification(_Serializer, Generic[T]):
    __LABELS = [ "mts", "type", "message_id", "_PLACEHOLDER", "data", "code", "status", "text" ]

    def __init__(self, serializer: Optional[_Serializer] = None, is_iterable: bool = False):
        super().__init__("Notification", Notification, _Notification.__LABELS, IGNORE = [ "_PLACEHOLDER" ])

        self.serializer, self.is_iterable = serializer, is_iterable

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> Notification[T]:
        notification = cast(Notification[T], Notification(**dict(self._serialize(*values))))

        if isinstance(self.serializer, _Serializer):
            data = cast(List[Any], notification.data)

            if self.is_iterable == False:
                if len(data) == 1 and isinstance(data[0], list):
                    data = data[0]

                notification.data = cast(T, self.serializer.klass(**dict(self.serializer._serialize(*data, skip=skip))))
            else: notification.data = cast(T, [ self.serializer.klass(**dict(self.serializer._serialize(*sub_data, skip=skip))) for sub_data in data ])

        return notification