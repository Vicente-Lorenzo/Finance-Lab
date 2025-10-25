from typing import Callable
from functools import wraps
from time import perf_counter
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI
from Library.Utility import seconds_to_string

@dataclass(slots=True, kw_only=True)
class Timer(DataclassAPI):
    Start: float = field(default=None, init=True, repr=False)
    Stop: float = field(default=None, init=True, repr=False)

    def start(self):
        self.Start = perf_counter()
    def stop(self):
        self.Stop = perf_counter()
    def delta(self):
        return self.Stop - self.Start
    def result(self):
        return seconds_to_string(self.delta())

def timer(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from Library.Logging import HandlerAPI
        log = HandlerAPI()
        t = Timer()
        t.start()
        result = func(*args, **kwargs)
        t.stop()
        log.debug(lambda: f"Time @ {func.__name__}: {t.result()}")
        return result
    return wrapper
