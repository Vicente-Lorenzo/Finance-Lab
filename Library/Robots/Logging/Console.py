import time

from io import BytesIO
from typing import Callable

from Agents.Container.Enums import VerboseType
from Agents.Logging.Logging import LoggingAPI

class ConsoleAPI(LoggingAPI):

    _LIGHT_ORANGE = "\033[38;5;214m"
    _ORANGE = "\033[38;5;208m"
    _BLUE = "\033[38;5;27m"
    _YELLOW = "\033[38;5;226m"
    _RED = "\033[38;5;196m"
    _DARK_RED = "\033[38;5;197m"
    _GRAY = "\033[38;5;245m"
    _LIGHT_GRAY = "\033[38;5;240m"
    _WHITE = "\033[0m"

    def __init__(self,
                 class_name: str,
                 role_name: str,
                 system: str | None = None,
                 strategy: str | None = None,
                 broker: str | None = None,
                 group: str | None = None,
                 symbol: str | None = None,
                 timeframe: str | None = None):
        
        super().__init__(class_name, role_name, system, strategy, broker, group, symbol, timeframe)

    def _format(self, level: VerboseType, level_color: str):
        return (
            f"{level_color}{level.name}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._SYSTEM}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._STRATEGY}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._BROKER}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._GROUP}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._SYMBOL}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._TIMEFRAME}{ConsoleAPI._LIGHT_GRAY} - "
            f"{ConsoleAPI._WHITE}{self._role}{ConsoleAPI._LIGHT_GRAY}")

    def _static(self) -> None:
        self.__STATIC_LOG_ALERT: str = self._format(VerboseType.Alert, ConsoleAPI._LIGHT_ORANGE)
        self.__STATIC_LOG_DEBUG: str = self._format(VerboseType.Debug, ConsoleAPI._ORANGE)
        self.__STATIC_LOG_INFO: str = self._format(VerboseType.Info, ConsoleAPI._BLUE)
        self.__STATIC_LOG_WARNING: str = self._format(VerboseType.Warning, ConsoleAPI._YELLOW)
        self.__STATIC_LOG_ERROR: str = self._format(VerboseType.Error, ConsoleAPI._RED)
        self.__STATIC_LOG_CRITICAL: str = self._format(VerboseType.Critical, ConsoleAPI._DARK_RED)

    @staticmethod
    def _log(static_log: str, content_func: Callable[[], str | BytesIO]):
        print(f"{ConsoleAPI._WHITE}{time.strftime('%F %X')}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._WHITE}{static_log}{ConsoleAPI._LIGHT_GRAY} - {ConsoleAPI._GRAY}{content_func()}{ConsoleAPI._WHITE}")

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_ALERT, content_func)

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_INFO, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self.__STATIC_LOG_CRITICAL, content_func)