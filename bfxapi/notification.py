from typing import List, Dict, Union, Optional, Any, TypedDict, cast

from .labeler import _Serializer

class Notification(TypedDict):
    MTS: int
    TYPE: str 
    MESSAGE_ID: Optional[int]
    NOTIFY_INFO: Union[Dict[str, Any], List[Dict[str, Any]]]
    CODE: Optional[int]
    STATUS: str
    TEXT: str

class _Notification(_Serializer):
    __LABELS = [ "MTS", "TYPE", "MESSAGE_ID", "_PLACEHOLDER", "NOTIFY_INFO", "CODE", "STATUS", "TEXT" ]

    def __init__(self, serializer: Optional[_Serializer] = None, iterate: bool = False):
        super().__init__("Notification", _Notification.__LABELS, IGNORE = [ "_PLACEHOLDER" ])

        self.serializer, self.iterate = serializer, iterate

    def parse(self, *values: Any, skip: Optional[List[str]] = None) -> Notification:
        notification = dict(self._serialize(*values))

        if isinstance(self.serializer, _Serializer):
            if self.iterate == False:
                NOTIFY_INFO = notification["NOTIFY_INFO"]

                if len(NOTIFY_INFO) == 1 and isinstance(NOTIFY_INFO[0], list):
                    NOTIFY_INFO = NOTIFY_INFO[0]

                notification["NOTIFY_INFO"] = dict(self.serializer._serialize(*NOTIFY_INFO, skip=skip))
            else: notification["NOTIFY_INFO"] = [ dict(self.serializer._serialize(*data, skip=skip)) for data in notification["NOTIFY_INFO"] ]

        return cast(Notification, notification)