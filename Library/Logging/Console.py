from io import BytesIO
from typing import Callable

from Library.Logging import LoggingAPI
from Library.Classes import VerboseType

class ConsoleAPI(LoggingAPI):

    _GREEN: str = "\033[38;5;46m"
    _BLUE: str = "\033[38;5;33m"
    _YELLOW: str = "\033[38;5;226m"
    _ORANGE: str = "\033[38;5;208m"
    _RED: str = "\033[38;5;196m"
    _DARK_RED: str = "\033[38;5;197m"
    _GRAY: str = "\033[38;5;245m"
    _LIGHT_GRAY: str = "\033[38;5;240m"
    _WHITE: str = "\033[0m"

    @staticmethod
    def _format_tag(static: str, tag: str) -> str:
        static += f"{ConsoleAPI._WHITE}{tag}{ConsoleAPI._LIGHT_GRAY}"
        return static

    def _format_level(self, level: VerboseType, level_color: str) -> str:
        static = ""
        for shared_tag in LoggingAPI._SHARED_TAGS.values():
            static = ConsoleAPI._format_tag(static, shared_tag)
            static += " - "
        static += f"{level_color}{level.name}{ConsoleAPI._LIGHT_GRAY}"
        for custom_tag in self._CUSTOM_TAGS.values():
            static += " - "
            static = ConsoleAPI._format_tag(static, custom_tag)
        return static

    def _format(self) -> None:
        self._STATIC_LOG_DEBUG: str = self._format_level(VerboseType.Debug, ConsoleAPI._GREEN)
        self._STATIC_LOG_INFO: str = self._format_level(VerboseType.Info, ConsoleAPI._BLUE)
        self._STATIC_LOG_ALERT: str = self._format_level(VerboseType.Alert, ConsoleAPI._ORANGE)
        self._STATIC_LOG_WARNING: str = self._format_level(VerboseType.Warning, ConsoleAPI._YELLOW)
        self._STATIC_LOG_ERROR: str = self._format_level(VerboseType.Error, ConsoleAPI._RED)
        self._STATIC_LOG_CRITICAL: str = self._format_level(VerboseType.Critical, ConsoleAPI._DARK_RED)

    @staticmethod
    def _build_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        return f"{ConsoleAPI._WHITE}{LoggingAPI.timestamp()}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._WHITE}{static_log}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._GRAY}{content_func()}{ConsoleAPI._WHITE}"

    @staticmethod
    def _output_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        print(ConsoleAPI._build_log(static_log, content_func))

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_INFO, content_func)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ALERT, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_CRITICAL, content_func)
