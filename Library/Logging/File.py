from pathlib import Path
from typing import Callable
from datetime import datetime
from io import BytesIO, TextIOWrapper

from Library.Logging import VerboseType, LoggingAPI
from Library.Utility import datetime_to_string

class FileAPI(LoggingAPI):

    _BUFFER_LIMIT: int = 1e6
    _buffer: list[str] = []
    _buffer_size: int = 0

    _dir_path: Path = Path("Library") / Path("Logging") / Path("Logs")
    _file_path: Path = None
    _file: TextIOWrapper | None = None

    @staticmethod
    def _flush():
        FileAPI._file.writelines(FileAPI._buffer)
        FileAPI._file.flush()

    @staticmethod
    def _clear():
        FileAPI._buffer.clear()
        FileAPI._buffer_size = 0

    @classmethod
    def setup(cls, verbose: VerboseType, uid: list[str], **kwargs) -> None:
        super().setup(verbose, **kwargs)
        now = datetime.now()
        unique_date = datetime_to_string(dt=now, fmt="%Y-%m-%d")
        unique_time = datetime_to_string(dt=now, fmt="%H-%M-%S")
        cls._file_path = cls._dir_path / f"{'_'.join(uid)}_{unique_date}_{unique_time}.log"

    def _enter_(self):
        FileAPI._file = FileAPI._file_path.open("a", encoding="utf-8")

    def _exit_(self):
        if FileAPI._buffer_size:
            FileAPI._flush()
        FileAPI._clear()
        FileAPI._file.close()

    @staticmethod
    def _format_tag(static: str, tag: str) -> str:
        static += f"{tag}"
        return static

    def _format_level(self, level: VerboseType) -> str:
        static = ""
        for base_tag in LoggingAPI._base_tags.values():
            static = FileAPI._format_tag(static, base_tag)
            static += " - "
        for class_tag in FileAPI._class_tags.values():
            static = FileAPI._format_tag(static, class_tag)
            static += " - "
        static += f"{level.name}"
        for instance_tags in self._instance_tags.values():
            static += " - "
            static = FileAPI._format_tag(static, instance_tags)
        return static

    def _format(self) -> None:
        self._static_log_debug: str = self._format_level(VerboseType.Debug)
        self._static_log_info: str = self._format_level(VerboseType.Info)
        self._static_log_alert: str = self._format_level(VerboseType.Alert)
        self._static_log_warning: str = self._format_level(VerboseType.Warning)
        self._static_log_error: str = self._format_level(VerboseType.Error)
        self._static_log_exception: str = self._format_level(VerboseType.Exception)

    @staticmethod
    def _build_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        return f"{LoggingAPI.timestamp()} - {static_log} - {content_func()}\n"

    @staticmethod
    def _output_log(static_log: str, content_func: Callable[[], str | BytesIO]):
        log = FileAPI._build_log(static_log, content_func)
        FileAPI._buffer.append(log)
        FileAPI._buffer_size += len(log)
        if FileAPI._buffer_size >= FileAPI._BUFFER_LIMIT:
            FileAPI._flush()
            FileAPI._clear()

    def _debug(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_debug, content_func)

    def _info(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_info, content_func)

    def _alert(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_alert, content_func)

    def _warning(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_warning, content_func)

    def _error(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_error, content_func)

    def _exception(self, content_func: Callable[[], str | BytesIO]):
        self._log(self._static_log_exception, content_func)
