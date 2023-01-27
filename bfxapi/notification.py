from typing import List, Dict, Union, Optional, Any, TypedDict, Generic, TypeVar, cast

from dataclasses import dataclass

from .labeler import _Type, _Serializer

T = TypeVar("T")

@dataclass
class Notification(_Type, Generic[T]):
    mts: int
    type: str 
    message_id: Optional[int]
    notify_info: T
    code: Optional[int]
    status: str
    text: str

class _Notification(_Serializer, Generic[T]):
    __LABELS = [ "mts", "type", "message_id", "_PLACEHOLDER", "notify_info", "code", "status", "text" ]

    def __init__(self, serializer: Optional[_Serializer] = None, iterate: bool = False):
        super().__init__("Notification", Notification, _Notification.__LABELS, IGNORE = [ "_PLACEHOLDER" ])

        self.serializer, self.iterate = serializer, iterate

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> Notification[T]:
        notification = cast(Notification[T], Notification(**dict(self._serialize(*values))))

        if isinstance(self.serializer, _Serializer):
            NOTIFY_INFO = cast(List[Any], notification.notify_info)

            if self.iterate == False:
                if len(NOTIFY_INFO) == 1 and isinstance(NOTIFY_INFO[0], list):
                    NOTIFY_INFO = NOTIFY_INFO[0]

                notification.notify_info = cast(T, self.serializer.klass(**dict(self.serializer._serialize(*NOTIFY_INFO, skip=skip))))
            else: notification.notify_info = cast(T, [ self.serializer.klass(**dict(self.serializer._serialize(*data, skip=skip))) for data in NOTIFY_INFO ])

        return notification