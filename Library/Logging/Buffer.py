from threading import Lock
from collections import deque
from Library.Logging import LoggingAPI, VerboseLevel

class BufferLoggingAPI(LoggingAPI):

    _buffer_: deque[str] = None
    _buffer_lock_: Lock = None

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        cls._buffer_ = deque()
        cls._buffer_lock_ = Lock()
        cls.enable_logging()

    @staticmethod
    def _format_tag_(tag: str, separator: bool = False) -> str:
        return tag

    @classmethod
    def _buffer_size_(cls) -> int:
        with cls._buffer_lock_:
            return len(cls._buffer_)

    @classmethod
    def _buffer_pushone_(cls, log: str) -> None:
        with cls._buffer_lock_:
            cls._buffer_.append(log)

    @classmethod
    def _buffer_pullone_(cls) -> str | None:
        with cls._buffer_lock_:
            return cls._buffer_.popleft() if cls._buffer_ else None

    @classmethod
    def _buffer_pullmany_(cls, n: int) -> list[str]:
        logs = []
        with cls._buffer_lock_:
            for _ in range(min(n, cls._buffer_size_())):
                logs.append(cls._buffer_.popleft())
        return logs

    @classmethod
    def _buffer_pullall_(cls) -> list[str]:
        with cls._buffer_lock_:
            logs = list(cls._buffer_)
            cls._buffer_.clear()
        return logs

    @classmethod
    def _buffer_clear_(cls) -> None:
        with cls._buffer_lock_:
            cls._buffer_.clear()

    @classmethod
    def _output_log_(cls, verbose: VerboseLevel, log: str) -> None:
        return cls._buffer_pushone_(log=log)
