from functools import lru_cache

def find_user():
    try:
        import getpass
        return getpass.getuser()
    except (OSError, KeyError, ImportError):
        import os
        return os.environ.get("USER") or os.environ.get("USERNAME")

def is_windows():
    import sys
    return sys.platform.startswith("win")

def is_linux():
    import sys
    return sys.platform.startswith("linux")

def is_mac():
    import sys
    return sys.platform.startswith("darwin")

def is_local():
    return is_windows() or is_mac()

def is_remote():
    return is_linux()

def is_service():
    return is_remote() and not find_user()

@lru_cache(maxsize=1)
def find_ipython():
    from IPython import get_ipython
    ipython = get_ipython()
    return ipython

@lru_cache(maxsize=1)
def find_shell():
    try:
        ipython = find_ipython()
        return type(ipython).__name__ if ipython else None
    except (ImportError, AttributeError):
        return None

def is_python():
    return find_shell() is None

def is_ipython():
    return find_shell() is not None

def is_notebook():
    return find_shell() == "ZMQInteractiveShell"

def is_terminal():
    return find_shell() == "TerminalInteractiveShell"

def is_console():
    return find_shell() == "PyDevTerminalInteractiveShell"

@lru_cache(maxsize=1)
def find_notebook():
    ipython = find_ipython()
    return ipython.user_ns["__session__"]
