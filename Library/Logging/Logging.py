from abc import ABC, abstractmethod
from typing import Callable
from io import BytesIO

from Library.Classes.Enums import VerboseType

class LoggingAPI(ABC):

    _DUMMY: Callable[[Callable[[], str]], None] = lambda *_: None

    _SYSTEM: str | None = None
    _STRATEGY: str | None = None
    _BROKER: str | None = None
    _GROUP: str | None = None
    _SYMBOL: str | None = None
    _TIMEFRAME: str | None = None

    _STATIC_LOG_ALERT: str | None = None
    _STATIC_LOG_DEBUG: str | None = None
    _STATIC_LOG_INFO: str | None = None
    _STATIC_LOG_WARNING: str | None = None
    _STATIC_LOG_ERROR: str | None = None
    _STATIC_LOG_CRITICAL: str | None = None

    alert: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    debug: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    info: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    warning: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    error: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    critical: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY

    def __init__(self,
                 class_name: str,
                 role_name: str,
                 system: str | None = None,
                 strategy: str | None = None,
                 broker: str | None = None,
                 group: str | None = None,
                 symbol: str | None = None,
                 timeframe: str | None = None):
        
        self._class: str = class_name
        self._role: str = role_name
        
        if system:
            self._SYSTEM = system
        if strategy:
            self._STRATEGY = strategy
        if broker:
            self._BROKER = broker
        if group:
            self._GROUP = group
        if symbol:
            self._SYMBOL = symbol
        if timeframe:
            self._TIMEFRAME = timeframe

        self._static()

    @staticmethod
    def init(system: str, strategy: str, broker: str, group: str, symbol: str, timeframe: str):
        LoggingAPI._SYSTEM = system
        LoggingAPI._STRATEGY = strategy
        LoggingAPI._BROKER = broker
        LoggingAPI._GROUP = group
        LoggingAPI._SYMBOL = symbol
        LoggingAPI._TIMEFRAME = timeframe

    @classmethod
    def level(cls, verbose: VerboseType):
        cls.alert = cls._alert if verbose.value >= VerboseType.Alert.value else LoggingAPI._DUMMY
        cls.debug = cls._debug if verbose.value >= VerboseType.Debug.value else LoggingAPI._DUMMY
        cls.info = cls._info if verbose.value >= VerboseType.Info.value else LoggingAPI._DUMMY
        cls.warning = cls._warning if verbose.value >= VerboseType.Warning.value else LoggingAPI._DUMMY
        cls.error = cls._error if verbose.value >= VerboseType.Error.value else LoggingAPI._DUMMY
        cls.critical = cls._critical if verbose.value >= VerboseType.Critical.value else LoggingAPI._DUMMY

    @abstractmethod
    def _format(self, *args) -> str:
        raise NotImplementedError

    @abstractmethod
    def _static(self) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _log(*args) -> None:
        raise NotImplementedError

    @abstractmethod
    def _alert(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError

    @abstractmethod
    def _debug(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError

    @abstractmethod
    def _info(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError

    @abstractmethod
    def _warning(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError

    @abstractmethod
    def _error(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError

    @abstractmethod
    def _critical(self, content_func: Callable[[], str | BytesIO]) -> Callable[[Callable[[], str]], None]:
        raise NotImplementedError