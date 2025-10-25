import io
import pstats
import cProfile

from typing import Callable
from functools import wraps
from datetime import datetime

from Library.Utility import datetime_to_string

def profiler(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from Library.Logging import HandlerAPI
        log = HandlerAPI()
        timestamp = datetime_to_string(datetime.now(), "%Y%m%d-%H%M%S")
        with cProfile.Profile() as pr:
            result = func(*args, **kwargs)
        ps = pstats.Stats(pr, stream=io.StringIO())
        snapshot_path = f"profile-{timestamp}.pstat"
        ps.dump_stats(snapshot_path)
        log.warning(lambda: f"Profile @ {func.__name__}: Snapshot {snapshot_path}")
        return result
    return wrapper
