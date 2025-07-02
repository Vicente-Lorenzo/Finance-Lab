from io import BytesIO
from typing import Callable

from Library.Logging import LoggingAPI
from Library.Classes import VerboseType

class ConsoleAPI(LoggingAPI):

    _LIGHT_ORANGE: str = "\033[38;5;214m"
    _ORANGE: str = "\033[38;5;208m"
    _BLUE: str = "\033[38;5;27m"
    _YELLOW: str = "\033[38;5;226m"
    _RED: str = "\033[38;5;196m"
    _DARK_RED: str = "\033[38;5;197m"
    _GRAY: str = "\033[38;5;245m"
    _LIGHT_GRAY: str = "\033[38;5;240m"
    _WHITE: str = "\033[0m"

    @classmethod
    def init(cls):
        super().init()

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super().__exit__(exc_type, exc_val, exc_tb)

    def _format(self, level: VerboseType, level_color: str) -> str:
        static = f"{level_color}{level.name}{ConsoleAPI._LIGHT_GRAY}"
        def add_metadata(s: str, md: str) -> str:
            s += f" - {ConsoleAPI._WHITE}{md}{ConsoleAPI._LIGHT_GRAY}"
            return s
        for metadata in LoggingAPI._META.values():
            static = add_metadata(static, metadata)
        if self._class:
            static = add_metadata(static, self._class)
        if self._subclass:
            static = add_metadata(static, self._subclass)
        return static

    def _format_logs(self) -> None:
        self._STATIC_LOG_ALERT: str = self._format(VerboseType.Alert, ConsoleAPI._LIGHT_ORANGE)
        self._STATIC_LOG_DEBUG: str = self._format(VerboseType.Debug, ConsoleAPI._ORANGE)
        self._STATIC_LOG_INFO: str = self._format(VerboseType.Info, ConsoleAPI._BLUE)
        self._STATIC_LOG_WARNING: str = self._format(VerboseType.Warning, ConsoleAPI._YELLOW)
        self._STATIC_LOG_ERROR: str = self._format(VerboseType.Error, ConsoleAPI._RED)
        self._STATIC_LOG_CRITICAL: str = self._format(VerboseType.Critical, ConsoleAPI._DARK_RED)

    @staticmethod
    def _build_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        return f"{ConsoleAPI._WHITE}{LoggingAPI.timestamp()}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._WHITE}{static_log}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._GRAY}{content_func()}{ConsoleAPI._WHITE}"

    @staticmethod
    def _output_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        print(ConsoleAPI._build_log(static_log, content_func))

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ALERT, content_func)

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_INFO, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_CRITICAL, content_func)
