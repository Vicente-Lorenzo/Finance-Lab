import io
import pstats
import cProfile

from typing import Callable
from functools import wraps
from time import perf_counter
from datetime import datetime

from Library.Utils import datetime_to_string, seconds_to_string

def timer(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from Library.Logging import HandlerAPI
        log = HandlerAPI(Class="Utils", Subclass=f"Performance")
        start_time = perf_counter()
        result = func(*args, **kwargs)
        stop_time = perf_counter()
        time_delta = stop_time - start_time
        log.debug(lambda: f"Time @ {func.__name__}: {seconds_to_string(time_delta)}")
        return result
    return wrapper

def profiler(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from Library.Logging import HandlerAPI
        log = HandlerAPI(Class="Utils", Subclass=f"Performance")
        timestamp = datetime_to_string(datetime.now(), "%Y%m%d-%H%M%S")
        with cProfile.Profile() as pr:
            result = func(*args, **kwargs)
        ps = pstats.Stats(pr, stream=io.StringIO())
        snapshot_path = f"profile-{timestamp}.pstat"
        ps.dump_stats(snapshot_path)
        log = HandlerAPI(Class="Performance", Subclass=f"")
        log.debug(lambda: f"Profile @ {func.__name__}: Snapshot {snapshot_path}")
        return result
    return wrapper
