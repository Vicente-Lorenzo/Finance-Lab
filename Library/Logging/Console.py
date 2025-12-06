from Library.Logging import VerboseLevel, LoggingAPI

class ConsoleLoggingAPI(LoggingAPI):

    _GREEN_: str = "\033[38;5;46m"
    _BLUE_: str = "\033[38;5;33m"
    _YELLOW_: str = "\033[38;5;226m"
    _ORANGE_: str = "\033[38;5;208m"
    _RED_: str = "\033[38;5;196m"
    _DARKRED_: str = "\033[38;5;197m"
    _GRAY_: str = "\033[38;5;245m"
    _LIGHTGRAY_: str = "\033[38;5;240m"
    _WHITE_: str = "\033[0m"

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        cls.enable_logging()

    @staticmethod
    def _format_tag_(tag: str,  separator: bool = False, color: str = _WHITE_, default: str = _WHITE_) -> str:
        color = ConsoleLoggingAPI._LIGHTGRAY_ if separator else color
        return f"{color}{tag}{default}"

    @classmethod
    def _set_class_verbose_tags_(cls) -> None:
        cls._class_debug_tag_ = cls._format_tag_(tag=VerboseLevel.Debug.name, color=cls._GREEN_)
        cls._class_info_tag_ = cls._format_tag_(tag=VerboseLevel.Info.name, color=cls._BLUE_)
        cls._class_alert_tag_ = cls._format_tag_(tag=VerboseLevel.Alert.name, color=cls._ORANGE_)
        cls._class_warning_tag_ = cls._format_tag_(tag=VerboseLevel.Warning.name, color=cls._YELLOW_)
        cls._class_error_tag_ = cls._format_tag_(tag=VerboseLevel.Error.name, color=cls._RED_)
        cls._class_exception_tag_ = cls._format_tag_(tag=VerboseLevel.Exception.name, color=cls._DARKRED_)

    @classmethod
    def _output_log_(cls, verbose: VerboseLevel, log: str) -> None:
        print(log)
