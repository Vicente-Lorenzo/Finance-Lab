from io import BytesIO
from typing import Callable

from Library.Logging import *

class HandlerAPI:

    def __init__(self, **kwargs):
        self.console = ConsoleAPI(**kwargs)
        self.telegram = TelegramAPI(**kwargs)
        self.file = FileAPI(**kwargs)

    def debug(self, content_func: Callable[[], str | BytesIO]):
        self.console.debug(content_func)
        self.telegram.debug(content_func)
        self.file.debug(content_func)

    def info(self, content_func: Callable[[], str | BytesIO]):
        self.console.info(content_func)
        self.telegram.info(content_func)
        self.file.info(content_func)

    def alert(self, content_func: Callable[[], str | BytesIO]):
        self.console.alert(content_func)
        self.telegram.alert(content_func)
        self.file.alert(content_func)

    def warning(self, content_func: Callable[[], str | BytesIO]):
        self.console.warning(content_func)
        self.telegram.warning(content_func)
        self.file.warning(content_func)

    def error(self, content_func: Callable[[], str | BytesIO]):
        self.console.error(content_func)
        self.telegram.error(content_func)
        self.file.error(content_func)

    def critical(self, content_func: Callable[[], str | BytesIO]):
        self.console.critical(content_func)
        self.telegram.critical(content_func)
        self.file.critical(content_func)

    def __enter__(self):
        self.console.__enter__()
        self.telegram.__enter__()
        self.file.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.console.__exit__(exc_type, exc_value, exc_traceback)
        self.telegram.__exit__(exc_type, exc_value, exc_traceback)
        self.file.__exit__(exc_type, exc_value, exc_traceback)
        return self
