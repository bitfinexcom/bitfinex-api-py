import sys
from copy import copy
from logging import FileHandler, Formatter, Logger, LogRecord, StreamHandler
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    _Level = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_BLACK, _RED, _GREEN, _YELLOW, _BLUE, _MAGENTA, _CYAN, _WHITE = [
    f"\033[0;{90 + i}m" for i in range(8)
]

(
    _BOLD_BLACK,
    _BOLD_RED,
    _BOLD_GREEN,
    _BOLD_YELLOW,
    _BOLD_BLUE,
    _BOLD_MAGENTA,
    _BOLD_CYAN,
    _BOLD_WHITE,
) = [f"\033[1;{90 + i}m" for i in range(8)]

_NC = "\033[0m"


class _ColorFormatter(Formatter):
    __LEVELS = {
        "INFO": _BLUE,
        "WARNING": _YELLOW,
        "ERROR": _RED,
        "CRITICAL": _BOLD_RED,
        "DEBUG": _BOLD_WHITE,
    }

    def format(self, record: LogRecord) -> str:
        _record = copy(record)
        _record.name = _MAGENTA + record.name + _NC
        _record.levelname = _ColorFormatter.__format_level(record.levelname)

        return super().format(_record)

    def formatTime(self, record: LogRecord, datefmt: Optional[str] = None) -> str:
        return _GREEN + super().formatTime(record, datefmt) + _NC

    @staticmethod
    def __format_level(level: str) -> str:
        return _ColorFormatter.__LEVELS[level] + level + _NC


_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

_DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


class ColorLogger(Logger):
    __FORMATTER = Formatter(_FORMAT, _DATE_FORMAT)

    def __init__(self, name: str, level: "_Level" = "NOTSET") -> None:
        super().__init__(name, level)

        formatter = _ColorFormatter(_FORMAT, _DATE_FORMAT)

        handler = StreamHandler(stream=sys.stderr)
        handler.setFormatter(fmt=formatter)
        self.addHandler(hdlr=handler)

    def register(self, filename: str) -> None:
        handler = FileHandler(filename=filename)
        handler.setFormatter(fmt=ColorLogger.__FORMATTER)
        self.addHandler(hdlr=handler)
