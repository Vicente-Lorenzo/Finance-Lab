from abc import ABC
from Library.Logging import VerboseLevel, LoggingAPI

class ReportLoggingAPI(LoggingAPI, ABC):

    _SUCCESS_TAG_ = "[✔️Success✔️]"
    _FAILURE_TAG_ = "[❌Failure❌]"

    _class_success_flag_ = None
    _class_failure_flag_ = None
    _class_verbose_threshold_: VerboseLevel = None

    @classmethod
    def _setup_class_(cls) -> None:
        cls.set_verbose_level(VerboseLevel.Silent, default=True)
        cls.set_threshold_level(VerboseLevel.Exception)
        cls.disable_success_report()
        cls.enable_failure_report()
        cls.enable_logging()

    @classmethod
    def is_success_report_enabled(cls) -> bool:
        with cls._class_lock_:
            return cls._class_success_flag_

    @classmethod
    def enable_success_report(cls) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._class_success_flag_ = True

    @classmethod
    def disable_success_report(cls) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._class_success_flag_ = False

    @classmethod
    def is_failure_report_enabled(cls) -> bool:
        with cls._class_lock_:
            return cls._class_failure_flag_

    @classmethod
    def enable_failure_report(cls) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._class_failure_flag_ = True

    @classmethod
    def disable_failure_report(cls) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._class_failure_flag_ = False

    @classmethod
    def set_threshold_level(cls, threshold_verbose: VerboseLevel) -> None:
        with cls._class_lock_:
            if cls.is_entered(): return
            cls._class_verbose_threshold_ = threshold_verbose

    @classmethod
    def is_success_report(cls) -> bool:
        with cls._class_lock_:
            if not cls.is_success_report_enabled(): return False
            return cls._verbose_min_ and cls._verbose_min_.value > cls._class_verbose_threshold_.value

    @classmethod
    def is_failure_report(cls) -> bool:
        with cls._class_lock_:
            if not cls.is_failure_report_enabled(): return False
            return cls._verbose_min_ and cls._verbose_min_.value <= cls._class_verbose_threshold_.value
