from enum import Enum
from io import BytesIO
from typing import Callable
from abc import ABC, abstractmethod
from datetime import datetime
from threading import Lock

from Library.Utility import *
from Library.Statistics import Timer

class VerboseLevel(Enum):
    Silent = 0
    Exception = 1
    Error = 2
    Warning = 3
    Alert = 4
    Info = 5
    Debug = 6

class LoggingAPI(ABC):

    _lock_: Lock = Lock()
    _host_info_: str = "Local" if is_local() else "Remote"
    _exec_info_: str = "Python" if is_python() else "Notebook"
    _path_info_: str = traceback_origin_file_path(resolve=True)
    _user_info_: str = user if (user := find_user()) else "Team"
    _verbose_max_: VerboseLevel = None
    _verbose_min_: VerboseLevel = None

    _class_lock_: Lock = None
    class_timer: Timer = None

    _class_tags_: str = None
    _class_debug_tag_: str = None
    _class_info_tag_: str = None
    _class_alert_tag_: str = None
    _class_warning_tag_: str = None
    _class_error_tag_: str = None
    _class_exception_tag_: str = None

    _class_verbose_default_: VerboseLevel = None
    _class_verbose_current_: VerboseLevel = None

    _class_log_flag_: bool = None
    _class_enter_flag_: bool = None
    _class_exit_flag_: bool = None

    _instance_tags_: str = None

    _dummy_: Callable[[Callable[[], str]], None] = lambda *_: None
    debug: Callable[[Callable[[], str | BytesIO]], None] = None
    info: Callable[[Callable[[], str | BytesIO]], None] = None
    alert: Callable[[Callable[[], str | BytesIO]], None] = None
    warning: Callable[[Callable[[], str | BytesIO]], None] = None
    error: Callable[[Callable[[], str | BytesIO]], None] = None
    exception: Callable[[Callable[[], str | BytesIO]], None] = None

    @staticmethod
    def set_host_info(host_info: str) -> None:
        with LoggingAPI._lock_:
            LoggingAPI._host_info_ = host_info

    @staticmethod
    def set_exec_info(exec_info: str) -> None:
        with LoggingAPI._lock_:
            LoggingAPI._exec_info_ = exec_info

    @staticmethod
    def set_path_info(path_info: str) -> None:
        with LoggingAPI._lock_:
            LoggingAPI._path_info_ = path_info

    @staticmethod
    def set_user_info(user_info: str) -> None:
        with LoggingAPI._lock_:
            LoggingAPI._user_info_ = user_info

    @classmethod
    @abstractmethod
    def _setup_class_(cls) -> None:
        cls.set_verbose_level(VerboseLevel.Debug, default=True)

    def __init_subclass__(cls):
        cls._class_lock_ = Lock()
        cls.class_timer = Timer()
        cls._set_class_verbose_tags_()
        cls._setup_class_()

    def __init__(self, *args, **kwargs) -> None:
        self.set_instance_tags(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def _format_tag_(*args, **kwargs) -> str:
        raise NotImplementedError

    @classmethod
    def set_class_tags(cls, *args, **kwargs) -> None:
        with cls._class_lock_:
            if not (args or kwargs): return
            cls._class_tags_ = " - ".join([cls._format_tag_(tag=tag) for tag in (*args, *kwargs.values())])

    @classmethod
    def _set_class_verbose_tags_(cls) -> None:
        with cls._class_lock_:
            cls._class_debug_tag_ = cls._format_tag_(tag=VerboseLevel.Debug.name)
            cls._class_info_tag_ = cls._format_tag_(tag=VerboseLevel.Info.name)
            cls._class_alert_tag_ = cls._format_tag_(tag=VerboseLevel.Alert.name)
            cls._class_warning_tag_ = cls._format_tag_(tag=VerboseLevel.Warning.name)
            cls._class_error_tag_ = cls._format_tag_(tag=VerboseLevel.Error.name)
            cls._class_exception_tag_ = cls._format_tag_(tag=VerboseLevel.Exception.name)

    def set_instance_tags(self, *args, **kwargs) -> None:
        if not (args or kwargs): return
        separator = self._format_tag_(tag=" - ", separator=True)
        self._instance_tags_ = separator.join([self._format_tag_(tag=tag) for tag in (*args, *kwargs.values())])

    @classmethod
    def set_verbose_level(cls, verbose: VerboseLevel, default=False) -> None:
        with cls._class_lock_:
            if default:
                cls._class_verbose_default_ = verbose
            match verbose:
                case VerboseLevel.Debug:
                    cls.debug = cls._debug_
                    cls.info = cls._info_
                    cls.alert = cls._alert_
                    cls.warning = cls._warning_
                    cls.error = cls._error_
                    cls.exception = cls._exception_
                case VerboseLevel.Info:
                    cls.debug = cls._dummy_
                    cls.info = cls._info_
                    cls.alert = cls._alert_
                    cls.warning = cls._warning_
                    cls.error = cls._error_
                    cls.exception = cls._exception_
                case VerboseLevel.Alert:
                    cls.debug = cls._dummy_
                    cls.info = cls._dummy_
                    cls.alert = cls._alert_
                    cls.warning = cls._warning_
                    cls.error = cls._error_
                    cls.exception = cls._exception_
                case VerboseLevel.Warning:
                    cls.debug = cls._dummy_
                    cls.info = cls._dummy_
                    cls.alert = cls._dummy_
                    cls.warning = cls._warning_
                    cls.error = cls._error_
                    cls.exception = cls._exception_
                case VerboseLevel.Error:
                    cls.debug = cls._dummy_
                    cls.info = cls._dummy_
                    cls.alert = cls._dummy_
                    cls.warning = cls._dummy_
                    cls.error = cls._error_
                    cls.exception = cls._exception_
                case VerboseLevel.Exception:
                    cls.debug = cls._dummy_
                    cls.info = cls._dummy_
                    cls.alert = cls._dummy_
                    cls.warning = cls._dummy_
                    cls.error = cls._dummy_
                    cls.exception = cls._exception_
                case VerboseLevel.Silent:
                    cls.debug = cls._dummy_
                    cls.info = cls._dummy_
                    cls.alert = cls._dummy_
                    cls.warning = cls._dummy_
                    cls.error = cls._dummy_
                    cls.exception = cls._dummy_
            cls._class_verbose_current_ = verbose

    @classmethod
    def reset_verbose_level(cls) -> None:
        cls.set_verbose_level(cls._class_verbose_default_)

    @classmethod
    def is_enabled(cls) -> bool:
        with cls._class_lock_:
            return cls._class_log_flag_

    @classmethod
    def enable_logging(cls) -> None:
        with cls._class_lock_:
            cls._class_log_flag_ = True

    @classmethod
    def disable_logging(cls) -> None:
        with cls._class_lock_:
            cls._class_log_flag_ = False

    @classmethod
    def is_entered(cls):
        with cls._class_lock_:
            return cls._class_enter_flag_

    @classmethod
    def enable_entering(cls) -> None:
        with cls._class_lock_:
            cls._class_enter_flag_ = False

    @classmethod
    def disable_entering(cls) -> None:
        with cls._class_lock_:
            cls._class_enter_flag_ = True

    @classmethod
    def is_exited(cls):
        with cls._class_lock_:
            return not cls._class_exit_flag_

    @classmethod
    def enable_exiting(cls) -> None:
        with cls._class_lock_:
            cls._class_exit_flag_ = True

    @classmethod
    def disable_exiting(cls) -> None:
        with cls._class_lock_:
            cls._class_exit_flag_ = False

    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def timestamp() -> str:
        return LoggingAPI.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _build_log_(self, level_tag: str = None, message: str = None) -> str:
        log = self._format_tag_(tag=self.timestamp())
        separator = self._format_tag_(tag=" - ", separator=True)
        if self._class_tags_ is not None:
            log += separator
            log += self._class_tags_
        if level_tag is not None:
            log += separator
            log += level_tag
        if self._instance_tags_ is not None:
            log += separator
            log += self._instance_tags_
        if message is not None:
            message_tag = self._format_tag_(tag=message)
            log += separator
            log += message_tag
        return log

    @classmethod
    @abstractmethod
    def _output_log_(cls, verbose: VerboseLevel, log: str) -> None:
        raise NotImplementedError

    def _log_(self, verbose: VerboseLevel, level_tag: str, content: Callable[[], str | BytesIO] | str) -> None:
        cls = self.__class__
        with LoggingAPI._lock_:
            if LoggingAPI._verbose_max_ is None or verbose.value > LoggingAPI._verbose_max_.value:
                LoggingAPI._verbose_max_ = verbose
            if LoggingAPI._verbose_min_ is None or verbose.value < LoggingAPI._verbose_min_.value:
                LoggingAPI._verbose_min_ = verbose
        with cls._class_lock_:
            if not cls.is_enabled(): return
            message = content() if isinstance(content, Callable) else content
            log = self._build_log_(level_tag=level_tag, message=message)
            cls._output_log_(verbose=verbose, log=log)

    def _debug_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Debug, self._class_debug_tag_, content)

    def _info_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Info, self._class_info_tag_, content)

    def _alert_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Alert, self._class_alert_tag_, content)

    def _warning_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Warning, self._class_warning_tag_, content)

    def _error_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Error, self._class_error_tag_, content)

    def _exception_(self, content: Callable[[], str | BytesIO] | str) -> None:
        self._log_(VerboseLevel.Exception, self._class_exception_tag_, content)

    def _enter_(self) -> None:
        pass

    def __enter__(self):
        cls = self.__class__
        with cls._class_lock_:
            if not cls.is_entered():
                cls.class_timer.start()
                self._enter_()
                cls.disable_entering()
                self.enable_exiting()
        return self

    def _exit_(self) -> None:
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        cls = self.__class__
        with cls._class_lock_:
            if not self.is_exited():
                cls.class_timer.stop()
                self._exit_()
                cls.enable_entering()
                self.disable_exiting()
        return self
