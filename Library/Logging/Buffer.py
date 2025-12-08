from threading import RLock
from collections import deque

from Library.Logging import VerboseLevel, LoggingAPI

class BufferLoggingAPI(LoggingAPI):

    _buffer_: deque[str] = None
    _buffer_lock_: RLock = None

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        cls.set_verbose_level(VerboseLevel.Silent, default=True)
        cls._buffer_ = deque()
        cls._buffer_lock_ = RLock()
        cls.enable_logging()

    @staticmethod
    def _format_tag_(tag: str, separator: bool = False) -> str:
        return tag

    @classmethod
    def output(cls, verbose: VerboseLevel, log) -> None:
        with cls._buffer_lock_:
            cls._buffer_.append(log)

    @classmethod
    def stream(cls) -> list:
        with cls._buffer_lock_:
            logs = list(cls._buffer_)
            cls._buffer_.clear()
            return logs
