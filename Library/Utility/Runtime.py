from functools import lru_cache
import sys

def is_windows():
    return sys.platform.startswith("win")

def is_linux():
    return sys.platform.startswith("linux")

def is_mac():
    return sys.platform.startswith("darwin")

def is_local():
    return is_windows() or is_mac()

def is_remote():
    return is_linux()

@lru_cache(maxsize=1)
def get_shell():
    try:
        from IPython import get_ipython
        shell = get_ipython()
        return type(shell).__name__ if shell else None
    except (ImportError, AttributeError):
        return None

def is_python():
    return get_shell() is None

def is_ipython():
    return get_shell() is not None

def is_notebook():
    return get_shell() == "ZMQInteractiveShell"

def is_terminal():
    return get_shell() == "TerminalInteractiveShell"

def is_console():
    return get_shell() == "PyDevTerminalInteractiveShell"
