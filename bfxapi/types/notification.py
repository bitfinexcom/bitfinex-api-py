from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar, cast

from .labeler import _Serializer, _Type

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
    __LABELS = [
        "mts",
        "type",
        "message_id",
        "_PLACEHOLDER",
        "data",
        "code",
        "status",
        "text",
    ]

    def __init__(
        self, serializer: Optional[_Serializer] = None, is_iterable: bool = False
    ):
        super().__init__("Notification", Notification, _Notification.__LABELS)

        self.serializer, self.is_iterable = serializer, is_iterable

    def parse(self, *values: Any) -> Notification[T]:
        notification = cast(
            Notification[T], Notification(**dict(self._serialize(*values)))
        )

        if isinstance(self.serializer, _Serializer):
            data = cast(List[Any], notification.data)

            if not self.is_iterable:
                if len(data) == 1 and isinstance(data[0], list):
                    data = data[0]

                notification.data = self.serializer.parse(*data)
            else:
                notification.data = cast(
                    T, [self.serializer.parse(*sub_data) for sub_data in data]
                )

        return notification
