from dash import html

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

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        cls.set_verbose_level(VerboseLevel.Silent, default=True)

    @staticmethod
    def _format_tag_(tag: str, color: str = _BLACK_, separator: bool = False) -> html.Span:
        color = WebLoggingAPI._LIGHTGRAY_ if separator else color
        return html.Span(tag, style={"color": color, "font-family": "Consolas"})

    @classmethod
    def _join_tags(cls, tags: list):
        separator = cls._format_tag_(tag=" - ", separator=True)
        result = []
        for tag in tags:
            if isinstance(tag, list):
                result.extend(tag)
            else:
                result.append(tag)
            result.append(separator)
        result.pop()
        return result

    @classmethod
    def _set_class_verbose_tags_(cls) -> None:
        cls._class_debug_tag_ = cls._format_tag_(tag=VerboseLevel.Debug.name, color=cls._GREEN_)
        cls._class_info_tag_ = cls._format_tag_(tag=VerboseLevel.Info.name, color=cls._BLUE_)
        cls._class_alert_tag_ = cls._format_tag_(tag=VerboseLevel.Alert.name, color=cls._ORANGE_)
        cls._class_warning_tag_ = cls._format_tag_(tag=VerboseLevel.Warning.name, color=cls._YELLOW_)
        cls._class_error_tag_ = cls._format_tag_(tag=VerboseLevel.Error.name, color=cls._RED_)
        cls._class_exception_tag_ = cls._format_tag_(tag=VerboseLevel.Exception.name, color=cls._DARKRED_)

    @classmethod
    def output(cls, verbose: VerboseLevel, log) -> None:
        return super().output(verbose=verbose, log=html.Div([*log, html.Br()]))
