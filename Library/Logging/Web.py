from Library.Utility import HTML
from Library.Logging import VerboseLevel, BufferLoggingAPI

class WebLoggingAPI(BufferLoggingAPI):

    _GREEN_ = "#00FF00"
    _BLUE_ = "#0087FF"
    _YELLOW_ = "#FFFF00"
    _ORANGE_ = "#FF8700"
    _RED_ = "#FF0000"
    _DARKRED_ = "#FF005F"
    _GRAY_ = "#8A8A8A"
    _LIGHTGRAY_ = "#585858"
    _BLACK_ = "#000000"

    @staticmethod
    def _format_tag_(tag: str, color: str = _BLACK_, separator: bool = False) -> str:
        color = WebLoggingAPI._LIGHTGRAY_ if separator else color
        return HTML.span(content=tag, font_color=color, font_family="Consolas")

    @classmethod
    def _set_class_verbose_tags_(cls) -> None:
        cls._class_debug_tag_ = cls._format_tag_(tag=VerboseLevel.Debug.name, color=cls._GREEN_)
        cls._class_info_tag_ = cls._format_tag_(tag=VerboseLevel.Info.name, color=cls._BLUE_)
        cls._class_alert_tag_ = cls._format_tag_(tag=VerboseLevel.Alert.name, color=cls._ORANGE_)
        cls._class_warning_tag_ = cls._format_tag_(tag=VerboseLevel.Warning.name, color=cls._YELLOW_)
        cls._class_error_tag_ = cls._format_tag_(tag=VerboseLevel.Error.name, color=cls._RED_)
        cls._class_exception_tag_ = cls._format_tag_(tag=VerboseLevel.Exception.name, color=cls._DARKRED_)

    @classmethod
    def output(cls, verbose: VerboseLevel, log: str) -> None:
        return super().output(verbose=verbose, log=log + HTML.blank_line() + "\n")
