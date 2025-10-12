from io import BytesIO
from typing import Callable

from Library.Logging import VerboseType, LoggingAPI

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
        for base_tag in LoggingAPI._base_tags.values():
            static = ConsoleAPI._format_tag(static, base_tag)
            static += " - "
        for class_tag in ConsoleAPI._class_tags.values():
            static = ConsoleAPI._format_tag(static, class_tag)
            static += " - "
        static += f"{level_color}{level.name}{ConsoleAPI._LIGHT_GRAY}"
        for instance_tags in self._instance_tags.values():
            static += " - "
            static = ConsoleAPI._format_tag(static, instance_tags)
        return static

    def _format(self) -> None:
        self._static_log_debug: str = self._format_level(VerboseType.Debug, ConsoleAPI._GREEN)
        self._static_log_info: str = self._format_level(VerboseType.Info, ConsoleAPI._BLUE)
        self._static_log_alert: str = self._format_level(VerboseType.Alert, ConsoleAPI._ORANGE)
        self._static_log_warning: str = self._format_level(VerboseType.Warning, ConsoleAPI._YELLOW)
        self._static_log_error: str = self._format_level(VerboseType.Error, ConsoleAPI._RED)
        self._static_log_exception: str = self._format_level(VerboseType.Exception, ConsoleAPI._DARK_RED)

    @staticmethod
    def _build_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        return f"{ConsoleAPI._WHITE}{LoggingAPI.timestamp()}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._WHITE}{static_log}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._GRAY}{content_func()}{ConsoleAPI._WHITE}"

    @staticmethod
    def _output_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        print(ConsoleAPI._build_log(static_log, content_func))

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_debug, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_info, content_func)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_alert, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_warning, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_error, content_func)

    def _exception(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_exception, content_func)
