import requests

from io import BytesIO
from typing import Callable

from Library.Logging import LoggingAPI
from Library.Classes import VerboseType, Telegram

class TelegramAPI(LoggingAPI):

    _DEBUG_ICON: str = "⚙️"
    _INFO_ICON: str = "ℹ️"
    _ALERT_ICON: str = "🔔"
    _WARNING_ICON: str = "⚠️"
    _ERROR_ICON: str = "❌"
    _CRITICAL_ICON: str = "🛑"
    
    _TIMESTAMP: str = "at {timestamp}"

    _LOG: Telegram = Telegram(Token="8183617727:AAGBFcbS104QXYczyB06UKA9StjCkK2RmRE", ChatID="-1002607268309")
    _LAB: Telegram = Telegram(Token="8032541880:AAFZEDPQPlVd6SVIcA7GohoiaK_-tNyW050", ChatID="-1002565200595")
    
    _GROUP: dict = {
        "Forex (Majors)": Telegram(Token="7180406910:AAG_JtWcwrFOdU0vrFo3u3YE60xJouCbDj8", ChatID="-1002557774416"),
        "Forex (Minors)": Telegram(Token="7858647408:AAH7M97_euohIMGX8X4gu3qtXbxKPBvHdHg", ChatID="-1002402990655"),
        "Forex (Exotics)": Telegram(Token="8020370305:AAF_XqDHIrp-QYkMT94DDjDd047SJZnQkvI", ChatID="-1002678006774"),
        "Stocks (US)": Telegram(Token="7621222262:AAHc1E-oQV7IFQhn8zecUU9awLhmYx72jc0", ChatID="-1002602965934"),
        "Stocks (EU)": Telegram(Token="7779184958:AAHnTVhELss3Oxy9wz8xgjoWl5--sU5BXp4", ChatID="-1002677954902"),
        "Metals": Telegram(Token="7955067039:AAFk26Be2Rip_IW26b-j0hpix1vJ3NWcAVM", ChatID="-1002683975427")}
    
    _MESSAGE_URL: str = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}"
    _DOCUMENT_URL: str = "https://api.telegram.org/bot{0}/sendDocument?chat_id={1}"

    _LOG_MESSAGE_URL: str = _MESSAGE_URL.format(_LOG.Token, _LOG.ChatID)
    _LOG_DOCUMENT_URL: str = _DOCUMENT_URL.format(_LOG.Token, _LOG.ChatID)

    _LAB_MESSAGE_URL: str = _MESSAGE_URL.format(_LAB.Token, _LAB.ChatID)
    _LAB_DOCUMENT_URL: str = _DOCUMENT_URL.format(_LAB.Token, _LAB.ChatID)

    _GROUP_MESSAGE_URL: str | None = None
    _GROUP_DOCUMENT_URL: str | None = None

    @classmethod
    def setup(cls, verbose: VerboseType, *args):
        super().setup(verbose)
        group_name = args[0]
        group = TelegramAPI._GROUP[group_name]
        cls._GROUP_MESSAGE_URL = TelegramAPI._MESSAGE_URL.format(group.Token, group.ChatID)
        cls._GROUP_DOCUMENT_URL = TelegramAPI._DOCUMENT_URL.format(group.Token, group.ChatID)

    @staticmethod
    def _format_tag(static: str, tag: str) -> str:
        static += f"<code>{tag.center(27)}</code>\n"
        return static

    def _format_level(self, level: VerboseType, level_icon: str) -> str:
        level_name = f" {level.name} "
        top_hline = f"{level_icon} {level_name.center(22, "-")} {level_icon}"
        middle_line = "-" * 28
        bottom_hline = f"{level_icon} {"-" * 22} {level_icon}"
        static = (
            f"<code>{top_hline}</code>\n"
            "<pre>{content}</pre>\n"
            f"<code>{middle_line}\n</code>"
        )
        for shared_tag in LoggingAPI._SHARED_TAGS.values():
            static = TelegramAPI._format_tag(static, shared_tag)
        for custom_tag in self._CUSTOM_TAGS.values():
            static = TelegramAPI._format_tag(static, custom_tag)
        static += (
            f"<code>{middle_line}\n</code>"
            "<code>{timestamp}</code>\n"
            f"<code>{bottom_hline}</code>"
        )
        return static

    def _format(self) -> None:
        self._STATIC_LOG_DEBUG: str = self._format_level(VerboseType.Debug, TelegramAPI._DEBUG_ICON)
        self._STATIC_LOG_INFO: str = self._format_level(VerboseType.Info, TelegramAPI._INFO_ICON)
        self._STATIC_LOG_ALERT: str = self._format_level(VerboseType.Alert, TelegramAPI._ALERT_ICON)
        self._STATIC_LOG_WARNING: str = self._format_level(VerboseType.Warning, TelegramAPI._WARNING_ICON)
        self._STATIC_LOG_ERROR: str = self._format_level(VerboseType.Error, TelegramAPI._ERROR_ICON)
        self._STATIC_LOG_CRITICAL: str = self._format_level(VerboseType.Critical, TelegramAPI._CRITICAL_ICON)

    @staticmethod
    def _build_log(message_url: str, document_url: str, static_log: str, content_func: Callable[[], str | BytesIO]):
        content = content_func()
        timestamp = TelegramAPI._TIMESTAMP.format(timestamp=LoggingAPI.timestamp())
        data = {"parse_mode": "html"}
        if isinstance(content, BytesIO):
            data["caption"] = timestamp
            files = {"document": ("image.png", content, "image/png")}
            return document_url, data, files
        else:
            data["text"] = static_log.format(content=content, timestamp=timestamp)
            return message_url, data, None

    @staticmethod
    def _output_log(message_url: str, document_url: str, static_log: str, content_func: Callable[[], str | BytesIO]):
        url, data, files = TelegramAPI._build_log(message_url, document_url, static_log, content_func)
        return requests.post(url, data=data, files=files)

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._LAB_MESSAGE_URL, self._LAB_DOCUMENT_URL, self._STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._LAB_MESSAGE_URL, self._LAB_DOCUMENT_URL, self._STATIC_LOG_INFO, content_func)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._GROUP_MESSAGE_URL, self._GROUP_DOCUMENT_URL, self._STATIC_LOG_ALERT, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._LOG_MESSAGE_URL, self._LOG_DOCUMENT_URL, self._STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._LOG_MESSAGE_URL, self._LOG_DOCUMENT_URL, self._STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._LOG_MESSAGE_URL, self._LOG_DOCUMENT_URL, self._STATIC_LOG_CRITICAL, content_func)
