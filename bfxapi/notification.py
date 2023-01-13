from typing import List, Dict, Union, Optional, Any, TypedDict, Generic, TypeVar, cast

from types import SimpleNamespace

from .labeler import _Serializer

T = TypeVar("T")

class Notification(SimpleNamespace, Generic[T]):
    MTS: int
    TYPE: str 
    MESSAGE_ID: Optional[int]
    NOTIFY_INFO: T
    CODE: Optional[int]
    STATUS: str
    TEXT: str

class _Notification(_Serializer, Generic[T]):
    __LABELS = [ "MTS", "TYPE", "MESSAGE_ID", "_PLACEHOLDER", "NOTIFY_INFO", "CODE", "STATUS", "TEXT" ]

    def __init__(self, serializer: Optional[_Serializer] = None, iterate: bool = False):
        super().__init__("Notification", _Notification.__LABELS, IGNORE = [ "_PLACEHOLDER" ])

        self.serializer, self.iterate = serializer, iterate

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> Notification[T]:
        notification = cast(Notification[T], SimpleNamespace(**dict(self._serialize(*values))))

        if isinstance(self.serializer, _Serializer):
            NOTIFY_INFO = cast(List[Any], notification.NOTIFY_INFO)

            if self.iterate == False:
                if len(NOTIFY_INFO) == 1 and isinstance(NOTIFY_INFO[0], list):
                    NOTIFY_INFO = NOTIFY_INFO[0]

                notification.NOTIFY_INFO = cast(T, SimpleNamespace(**dict(self.serializer._serialize(*NOTIFY_INFO, skip=skip))))
            else: notification.NOTIFY_INFO = cast(T, [ SimpleNamespace(**dict(self.serializer._serialize(*data, skip=skip))) for data in NOTIFY_INFO ])

        return notification