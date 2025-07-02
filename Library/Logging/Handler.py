from io import BytesIO
from typing import Callable

from Library.Logging import *

class HandlerAPI:

    logging: LoggingAPI
    console: ConsoleAPI | None = None
    telegram: TelegramAPI | None = None
    file: FileAPI | None = None

    def __init__(self, class_name: str | None = None, subclass_name: str | None = None, **kwargs):
        self.console = ConsoleAPI(class_name=class_name, subclass_name=subclass_name, **kwargs)
        self.telegram = TelegramAPI(class_name=class_name, subclass_name=subclass_name, **kwargs)
        self.file = FileAPI(class_name=class_name, subclass_name=subclass_name, **kwargs)

    def alert(self, content_func: Callable[[], str | BytesIO]):
        self.console.alert(content_func)
        self.telegram.alert(content_func)
        self.file.alert(content_func)

    def debug(self, content_func: Callable[[], str | BytesIO]):
        self.console.debug(content_func)
        self.telegram.debug(content_func)
        self.file.debug(content_func)

    def info(self, content_func: Callable[[], str | BytesIO]):
        self.console.info(content_func)
        self.telegram.info(content_func)
        self.file.info(content_func)

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.console.__exit__(exc_type, exc_val, exc_tb)
        self.telegram.__exit__(exc_type, exc_val, exc_tb)
        self.file.__exit__(exc_type, exc_val, exc_tb)
