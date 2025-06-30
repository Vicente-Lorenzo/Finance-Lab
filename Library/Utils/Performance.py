import io
import pstats
import cProfile

from functools import wraps
from time import perf_counter
from datetime import datetime

from Library.Logging.Console import ConsoleAPI
from Library.Utils import datetime_to_string

def time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        stop_time = perf_counter()
        console = ConsoleAPI(class_name="Performance", role_name=f"Time @ {func.__name__}")
        console.warning(lambda: f"{stop_time - start_time:.6f} seconds")
        return result
    return wrapper

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime_to_string(datetime.now(), "%Y%m%d-%H%M%S")
        with cProfile.Profile() as pr:
            result = func(*args, **kwargs)
        ps = pstats.Stats(pr, stream=io.StringIO())
        ps.dump_stats(f"profile-{timestamp}.pstat")
        console: ConsoleAPI = ConsoleAPI(class_name="Performance", role_name=f"Profile @ {func.__name__}")
        console.warning(lambda: f"Snapshot saved")
        return result
    return wrapper