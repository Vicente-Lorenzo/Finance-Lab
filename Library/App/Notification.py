from threading import RLock
from collections import deque

from Library.Logging import VerboseLevel
from Library.App.Component import Component, NotificationAPI

class NotifierAPI:

    _COLORS_ = {
        VerboseLevel.Debug: "level-debug",
        VerboseLevel.Info: "level-info",
        VerboseLevel.Alert: "level-alert",
        VerboseLevel.Warning: "level-warning",
        VerboseLevel.Error: "level-error",
        VerboseLevel.Exception: "level-exception"
    }

    _ICONS_ = {
        VerboseLevel.Debug: "bi bi-gear-fill",
        VerboseLevel.Info: "bi bi-info-circle-fill",
        VerboseLevel.Alert: "bi bi-bell-fill",
        VerboseLevel.Warning: "bi bi-exclamation-triangle-fill",
        VerboseLevel.Error: "bi bi-x-circle-fill",
        VerboseLevel.Exception: "bi bi-exclamation-octagon-fill"
    }

    def __init__(self, duration: int) -> None:
        self._buffer_: deque[Component] = deque()
        self._lock_: RLock = RLock()
        self._duration_: int = duration

    def _push_(self, verbose: VerboseLevel, message: str, duration: int = None) -> None:
        toast = NotificationAPI(
            element=message,
            header=verbose.name,
            icon=self._ICONS_.get(verbose, "bi bi-info-circle-fill"),
            background=self._COLORS_.get(verbose, "primary"),
            duration=duration if duration is not None else self._duration_
        ).build()
        with self._lock_:
            self._buffer_.extend(toast)

    def stream(self) -> list[Component]:
        with self._lock_:
            items = list(self._buffer_)
            self._buffer_.clear()
            return items

    def debug(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Debug, message, duration)

    def info(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Info, message, duration)

    def alert(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Alert, message, duration)

    def warning(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Warning, message, duration)

    def error(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Error, message, duration)

    def exception(self, message: str, duration: int = None) -> None:
        self._push_(VerboseLevel.Exception, message, duration)