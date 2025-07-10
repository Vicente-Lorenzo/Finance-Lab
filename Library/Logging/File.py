from pathlib import Path
from typing import Callable
from datetime import datetime
from io import BytesIO, TextIOWrapper

from Library.Classes import VerboseType
from Library.Logging import LoggingAPI
from Library.Utils import datetime_to_string

class FileAPI(LoggingAPI):

    _DIR_PATH: Path = Path("Library") / Path("Logging") / Path("Logs")
    _FILE_PATH: Path = None
    _BUFFER: list[str] = []
    _BUFFER_SIZE: int = 0
    _BUFFER_LIMIT: int = 1e6

    _UID: str | None = None
    _FILE: TextIOWrapper | None = None

    @staticmethod
    def _flush():
        FileAPI._FILE.writelines(FileAPI._BUFFER)
        FileAPI._FILE.flush()

    @staticmethod
    def _clear():
        FileAPI._BUFFER.clear()
        FileAPI._BUFFER_SIZE = 0

    @classmethod
    def setup(cls, verbose: VerboseType, *args):
        super().setup(verbose)
        now = datetime.now()
        unique_name = args[0]
        unique_date = datetime_to_string(dt=now, fmt="%Y-%m-%d")
        unique_time = datetime_to_string(dt=now, fmt="%H-%M-%S")
        cls._FILE_PATH = cls._DIR_PATH / f"{unique_name}_{unique_date}_{unique_time}.log"

    def __enter__(self):
        FileAPI._FILE = FileAPI._FILE_PATH.open("a", encoding="utf-8")
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if FileAPI._BUFFER_SIZE:
            FileAPI._flush()
        FileAPI._clear()
        FileAPI._FILE.close()
        return super().__exit__(exc_type, exc_value, exc_traceback)

    @staticmethod
    def _format_tag(static: str, tag: str) -> str:
        static += f"{tag}"
        return static

    def _format_level(self, level: VerboseType) -> str:
        static = ""
        for shared_tag in LoggingAPI._SHARED_TAGS.values():
            static = FileAPI._format_tag(static, shared_tag)
            static += " - "
        static += f"{level.name}"
        for custom_tag in self._CUSTOM_TAGS.values():
            static += " - "
            static = FileAPI._format_tag(static, custom_tag)
        return static

    def _format(self) -> None:
        self._STATIC_LOG_DEBUG: str = self._format_level(VerboseType.Debug)
        self._STATIC_LOG_INFO: str = self._format_level(VerboseType.Info)
        self._STATIC_LOG_ALERT: str = self._format_level(VerboseType.Alert)
        self._STATIC_LOG_WARNING: str = self._format_level(VerboseType.Warning)
        self._STATIC_LOG_ERROR: str = self._format_level(VerboseType.Error)
        self._STATIC_LOG_CRITICAL: str = self._format_level(VerboseType.Critical)

    @staticmethod
    def _build_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        return f"{LoggingAPI.timestamp()} - {static_log} - {content_func()}\n"

    @staticmethod
    def _output_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        log = FileAPI._build_log(static_log, content_func)
        FileAPI._BUFFER.append(log)
        FileAPI._BUFFER_SIZE += len(log)
        if FileAPI._BUFFER_SIZE >= FileAPI._BUFFER_LIMIT:
            FileAPI._flush()
            FileAPI._clear()

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_DEBUG, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_INFO, content_func)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ALERT, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_WARNING, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_ERROR, content_func)

    def _critical(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._STATIC_LOG_CRITICAL, content_func)
