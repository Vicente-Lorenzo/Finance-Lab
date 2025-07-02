import datetime
from io import BytesIO
from typing import Callable
from abc import ABC, abstractmethod
from threading import Lock

from Library.Classes import VerboseType
from Library.Utils.DateTime import datetime_to_string

class LoggingAPI(ABC):

    _META: dict = {}
    _DUMMY: Callable[[Callable[[], str]], None] = lambda *_: None

    _STATIC_LOG_ALERT: str | None = None
    _STATIC_LOG_DEBUG: str | None = None
    _STATIC_LOG_INFO: str | None = None
    _STATIC_LOG_WARNING: str | None = None
    _STATIC_LOG_ERROR: str | None = None
    _STATIC_LOG_CRITICAL: str | None = None

    _LOCK: Lock = None

    alert: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    debug: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    info: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    warning: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    error: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY
    critical: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY

    def __init__(self, class_name: str | None = None, subclass_name: str | None = None, **kwargs):
        self._class: str | None = class_name
        self._subclass: str | None = subclass_name
        self._META.update(kwargs)
        self._format_logs()

    @staticmethod
    def meta(**kwargs) -> None:
        LoggingAPI._META.clear()
        LoggingAPI._META.update(kwargs)

    @classmethod
    @abstractmethod
    def init(cls, *args, **kwargs):
        cls._LOCK = Lock()

    @classmethod
    def level(cls, verbose: VerboseType) -> None:
        cls.alert = cls._alert if verbose.value >= VerboseType.Alert.value else LoggingAPI._DUMMY
        cls.debug = cls._debug if verbose.value >= VerboseType.Debug.value else LoggingAPI._DUMMY
        cls.info = cls._info if verbose.value >= VerboseType.Info.value else LoggingAPI._DUMMY
        cls.warning = cls._warning if verbose.value >= VerboseType.Warning.value else LoggingAPI._DUMMY
        cls.error = cls._error if verbose.value >= VerboseType.Error.value else LoggingAPI._DUMMY
        cls.critical = cls._critical if verbose.value >= VerboseType.Critical.value else LoggingAPI._DUMMY

    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    @staticmethod
    def timestamp() -> str:
        return datetime_to_string(dt=datetime.datetime.now(), fmt="%Y-%m-%d %H:%M:%S.%f")[:-3]

    @abstractmethod
    def _format(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def _format_logs(self) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _build_log(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _output_log(*args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _log(cls, *args, **kwargs):
        with cls._LOCK:
            cls._output_log(*args, **kwargs)

    @abstractmethod
    def _alert(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _debug(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _info(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _warning(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _error(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _critical(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError
