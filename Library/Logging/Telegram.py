import time
import requests

from io import BytesIO
from typing import Callable

from Library.Logging.Logging import LoggingAPI
from Library.Classes.Enums import VerboseType
from Library.Classes.Classes import TelegramBot

class TelegramAPI(LoggingAPI):
    
    ALERT_ICON = "🔔"
    DEBUG_ICON = "⚙️"
    INFO_ICON = "ℹ️"
    WARNING_ICON = "⚠️"
    ERROR_ICON = "❌"
    CRITICAL_ICON = "🛑"
    
    TIMESTAMP = "Log at {timestamp}"

    LOG = TelegramBot(Token="8183617727:AAGBFcbS104QXYczyB06UKA9StjCkK2RmRE", ChatID="-1002607268309")
    LAB = TelegramBot(Token="8032541880:AAFZEDPQPlVd6SVIcA7GohoiaK_-tNyW050", ChatID="-1002565200595")
    
    GROUP= {
        "Forex (Majors)": TelegramBot(Token="7180406910:AAG_JtWcwrFOdU0vrFo3u3YE60xJouCbDj8", ChatID="-1002557774416"),
        "Forex (Minors)": TelegramBot(Token="7858647408:AAH7M97_euohIMGX8X4gu3qtXbxKPBvHdHg", ChatID="-1002402990655"),
        "Forex (Exotics)": TelegramBot(Token="8020370305:AAF_XqDHIrp-QYkMT94DDjDd047SJZnQkvI", ChatID="-1002678006774"),
        "Stocks (US)": TelegramBot(Token="7621222262:AAHc1E-oQV7IFQhn8zecUU9awLhmYx72jc0", ChatID="-1002602965934"),
        "Stocks (EU)": TelegramBot(Token="7779184958:AAHnTVhELss3Oxy9wz8xgjoWl5--sU5BXp4", ChatID="-1002677954902"),
        "Metals": TelegramBot(Token="7955067039:AAFk26Be2Rip_IW26b-j0hpix1vJ3NWcAVM", ChatID="-1002683975427")}
    
    MESSAGE_URL = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}"
    DOCUMENT_URL = "https://api.telegram.org/bot{0}/sendDocument?chat_id={1}"

    def __init__(self,
                 class_name: str,
                 role_name: str,
                 system: str | None = None,
                 strategy: str | None = None,
                 broker: str | None = None,
                 group: str | None = None,
                 symbol: str | None = None,
                 timeframe: str | None = None):
        
        super().__init__(class_name, role_name, system, strategy, broker, group, symbol, timeframe)
        
        self._log_message_url = TelegramAPI.MESSAGE_URL.format(TelegramAPI.LOG.Token, TelegramAPI.LOG.ChatID)
        self._log_document_url = TelegramAPI.DOCUMENT_URL.format(TelegramAPI.LOG.Token, TelegramAPI.LOG.ChatID)
        
        self._lab_message_url = TelegramAPI.MESSAGE_URL.format(TelegramAPI.LAB.Token, TelegramAPI.LAB.ChatID)
        self._lab_document_url = TelegramAPI.DOCUMENT_URL.format(TelegramAPI.LAB.Token, TelegramAPI.LAB.ChatID)
        
        group = TelegramAPI.GROUP[self._GROUP]
        self._group_message_url = TelegramAPI.MESSAGE_URL.format(group.Token, group.ChatID)
        self._group_document_url = TelegramAPI.DOCUMENT_URL.format(group.Token, group.ChatID)

    def _format(self, level: VerboseType, level_icon: str):
        level_name = f" {level.name} "
        top_hline = f"{level_icon} {level_name.center(22, "-")} {level_icon}"
        middle_line = "-" * 28
        bottom_hline = f"{level_icon} {"-" * 22} {level_icon}"
        return (
            f"<code>{top_hline}</code>\n"
            "<pre>{content}</pre>\n"
            f"<code>{middle_line}\n</code>"
            f"<code>{self._SYSTEM.center(27)}</code>\n"
            f"<code>{self._STRATEGY.center(27)}</code>\n"
            f"<code>{self._BROKER.center(27)}</code>\n"
            f"<code>{self._GROUP.center(27)}</code>\n"
            f"<code>{self._SYMBOL.center(27)}</code>\n"
            f"<code>{self._TIMEFRAME.center(27)}</code>\n"
            f"<code>{self._role.center(27)}</code>\n"
            f"<code>{middle_line}\n</code>"
            "<code>{timestamp}</code>\n"
            f"<code>{bottom_hline}</code>")

    def _static(self) -> None:
        self.__STATIC_LOG_ALERT: str = self._format(VerboseType.Alert, TelegramAPI.ALERT_ICON)
        self.__STATIC_LOG_DEBUG: str = self._format(VerboseType.Debug, TelegramAPI.DEBUG_ICON)
        self.__STATIC_LOG_INFO: str = self._format(VerboseType.Info, TelegramAPI.INFO_ICON)
        self.__STATIC_LOG_WARNING: str = self._format(VerboseType.Warning, TelegramAPI.WARNING_ICON)
        self.__STATIC_LOG_ERROR: str = self._format(VerboseType.Error, TelegramAPI.ERROR_ICON)
        self.__STATIC_LOG_CRITICAL: str = self._format(VerboseType.Critical, TelegramAPI.CRITICAL_ICON)

    @staticmethod
    def _log(message_url: str, document_url: str, static_log: str, content_func: Callable[[], str | BytesIO]):
        content = content_func()
        timestamp = TelegramAPI.TIMESTAMP.format(timestamp=time.strftime("%F %X"))
        data = {"parse_mode": "html"}
        if isinstance(content, BytesIO):
            data["caption"] = timestamp
            files = {"document": ("image.png", content, "image/png")}
            return requests.post(document_url, data=data, files=files)
        data["text"] = static_log.format(content=content, timestamp=timestamp)
        return requests.post(message_url, data=data)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._group_message_url, self._group_document_url, self.__STATIC_LOG_ALERT, content_func)

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._lab_message_url, self._lab_document_url, self.__STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._lab_message_url, self._lab_document_url, self.__STATIC_LOG_INFO, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._log_message_url, self._log_document_url, self.__STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._log_message_url, self._log_document_url, self.__STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._log_message_url, self._log_document_url, self.__STATIC_LOG_CRITICAL, content_func)