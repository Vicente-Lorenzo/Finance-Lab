import datetime
from io import BytesIO
from typing import Callable
from abc import ABC, abstractmethod
from threading import Lock

from Library.Classes import VerboseType
from Library.Utils.DateTime import datetime_to_string

class LoggingAPI(ABC):

    _default_verbose: VerboseType = VerboseType.Silent
    _current_verbose: VerboseType = VerboseType.Silent

    _base_tags: dict = {}
    _class_tags: dict = {}
    _instance_tags: dict = {}

    _static_log_debug: str | None = None
    _static_log_info: str | None = None
    _static_log_alert: str | None = None
    _static_log_warning: str | None = None
    _static_log_error: str | None = None
    _static_log_critical: str | None = None

    _lock: Lock = None

    _dummy: Callable[[Callable[[], str]], None] = lambda *_: None
    debug: Callable[[Callable[[], str | BytesIO]], None] = _dummy
    info: Callable[[Callable[[], str | BytesIO]], None] = _dummy
    alert: Callable[[Callable[[], str | BytesIO]], None] = _dummy
    warning: Callable[[Callable[[], str | BytesIO]], None] = _dummy
    error: Callable[[Callable[[], str | BytesIO]], None] = _dummy
    critical: Callable[[Callable[[], str | BytesIO]], None] = _dummy

    @staticmethod
    def init(**kwargs) -> None:
        LoggingAPI._base_tags.clear()
        LoggingAPI._base_tags.update(kwargs)

    @classmethod
    def setup(cls, verbose: VerboseType, **kwargs) -> None:
        cls._class_tags.clear()
        cls._class_tags.update(kwargs)
        cls._default_verbose = verbose
        cls._lock = Lock()
        cls.reset()

    def __init__(self, **kwargs):
        self._instance_tags.clear()
        for k, v in kwargs.items():
            if k in LoggingAPI._base_tags:
                self._base_tags[k] = v
            elif k in self.__class__._class_tags:
                self._class_tags[k] = v
            else:
                self._instance_tags[k] = v
        self._format()

    @classmethod
    def level(cls, verbose: VerboseType) -> None:
        with cls._lock:
            if verbose == cls._current_verbose:
                return
            match verbose:
                case VerboseType.Debug:
                    cls.debug = cls._debug
                    cls.info = cls._info
                    cls.alert = cls._alert
                    cls.warning = cls._warning
                    cls.error = cls._error
                    cls.critical = cls._critical
                case VerboseType.Info:
                    cls.debug = cls._dummy
                    cls.info = cls._info
                    cls.alert = cls._alert
                    cls.warning = cls._warning
                    cls.error = cls._error
                    cls.critical = cls._critical
                case VerboseType.Alert:
                    cls.debug = cls._dummy
                    cls.info = cls._dummy
                    cls.alert = cls._alert
                    cls.warning = cls._warning
                    cls.error = cls._error
                    cls.critical = cls._critical
                case VerboseType.Warning:
                    cls.debug = cls._dummy
                    cls.info = cls._dummy
                    cls.alert = cls._dummy
                    cls.warning = cls._warning
                    cls.error = cls._error
                    cls.critical = cls._critical
                case VerboseType.Error:
                    cls.debug = cls._dummy
                    cls.info = cls._dummy
                    cls.alert = cls._dummy
                    cls.warning = cls._dummy
                    cls.error = cls._error
                    cls.critical = cls._critical
                case VerboseType.Critical:
                    cls.debug = cls._dummy
                    cls.info = cls._dummy
                    cls.alert = cls._dummy
                    cls.warning = cls._dummy
                    cls.error = cls._dummy
                    cls.critical = cls._critical
                case VerboseType.Silent:
                    cls.debug = cls._dummy
                    cls.info = cls._dummy
                    cls.alert = cls._dummy
                    cls.warning = cls._dummy
                    cls.error = cls._dummy
                    cls.critical = cls._dummy
            cls._current_verbose = verbose

    @classmethod
    def reset(cls) -> None:
        cls.level(cls._default_verbose)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
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
        with cls._lock:
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
