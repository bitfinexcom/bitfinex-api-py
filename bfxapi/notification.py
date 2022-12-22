from typing import Dict, Optional, Any, TypedDict, cast

from .labeler import _Serializer

class Notification(TypedDict):
    MTS: int
    TYPE: str 
    MESSAGE_ID: Optional[int]
    NOTIFY_INFO: Dict[str, Any]
    CODE: Optional[int]
    STATUS: str
    TEXT: str

class _Notification(_Serializer):
    __LABELS = [ "MTS", "TYPE", "MESSAGE_ID", "_PLACEHOLDER", "NOTIFY_INFO", "CODE", "STATUS", "TEXT" ]

    def __init__(self, serializer: Optional[_Serializer] = None):
        super().__init__("Notification", _Notification.__LABELS, IGNORE = [ "_PLACEHOLDER" ])

        self.serializer = serializer

    def parse(self, *values: Any) -> Notification:
        notification = dict(self._serialize(*values))

        if self.serializer != None:
            notification["NOTIFY_INFO"] = dict(self.serializer._serialize(*notification["NOTIFY_INFO"]))
 
        return cast(Notification, notification)