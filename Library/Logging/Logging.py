import datetime
from io import BytesIO
from typing import Callable
from abc import ABC, abstractmethod
from threading import Lock

from Library.Classes import VerboseType
from Library.Utils.DateTime import datetime_to_string

class LoggingAPI(ABC):

    _SHARED_TAGS: dict = {}
    _CUSTOM_TAGS: dict = {}

    _DUMMY_LOG_FUNCTION: Callable[[Callable[[], str]], None] = lambda *_: None

    _STATIC_LOG_DEBUG: str | None = None
    _STATIC_LOG_INFO: str | None = None
    _STATIC_LOG_ALERT: str | None = None
    _STATIC_LOG_WARNING: str | None = None
    _STATIC_LOG_ERROR: str | None = None
    _STATIC_LOG_CRITICAL: str | None = None

    _LOCK: Lock = None

    debug: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION
    info: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION
    alert: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION
    warning: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION
    error: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION
    critical: Callable[[Callable[[], str | BytesIO]], None] = _DUMMY_LOG_FUNCTION

    @staticmethod
    def init(**kwargs) -> None:
        LoggingAPI._SHARED_TAGS.clear()
        LoggingAPI._SHARED_TAGS.update(kwargs)

    @classmethod
    def setup(cls, *args, **kwargs):
        cls._LOCK = Lock()

    @classmethod
    def level(cls, verbose: VerboseType) -> None:
        cls.debug = cls._debug if verbose.value >= VerboseType.Debug.value else LoggingAPI._DUMMY_LOG_FUNCTION
        cls.info = cls._info if verbose.value >= VerboseType.Info.value else LoggingAPI._DUMMY_LOG_FUNCTION
        cls.alert = cls._alert if verbose.value >= VerboseType.Alert.value else LoggingAPI._DUMMY_LOG_FUNCTION
        cls.warning = cls._warning if verbose.value >= VerboseType.Warning.value else LoggingAPI._DUMMY_LOG_FUNCTION
        cls.error = cls._error if verbose.value >= VerboseType.Error.value else LoggingAPI._DUMMY_LOG_FUNCTION
        cls.critical = cls._critical if verbose.value >= VerboseType.Critical.value else LoggingAPI._DUMMY_LOG_FUNCTION

    def __init__(self, **kwargs):
        self._CUSTOM_TAGS.clear()
        for k, v in kwargs.items():
            if k in LoggingAPI._SHARED_TAGS:
                self._SHARED_TAGS.update({k: v})
            else:
                self._CUSTOM_TAGS.update({k: v})
        self._format()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    @staticmethod
    def timestamp() -> str:
        return datetime_to_string(dt=datetime.datetime.now(), fmt="%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    @abstractmethod
    def _format_tag(static: str, tag: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _format_level(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def _format(self) -> None:
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
    def _debug(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _info(self, content_func: Callable[[], str | BytesIO]):
        raise NotImplementedError

    @abstractmethod
    def _alert(self, content_func: Callable[[], str | BytesIO]):
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
