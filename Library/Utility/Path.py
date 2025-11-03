from sys import _getframe
from pathlib import Path

def inspect_file(file: str | Path) -> Path:
    return Path(file).resolve()

def inspect_file_path(file: str | Path) -> str:
    return str(inspect_file(file))

def inspect_module(file: str | Path) -> Path:
    return inspect_file(file).parent

def inspect_module_path(file: str | Path) -> str:
    return inspect_file_path(inspect_module(file))

def traceback_file(frame: int) -> Path:
    return inspect_file(traceback_file_path(frame))

def traceback_file_path(frame: int) -> str:
    return _getframe(frame).f_code.co_filename

def traceback_module(frame: int) -> Path:
    return inspect_module(traceback_file_path(frame))

def traceback_module_path(frame: int) -> str:
    return inspect_module_path(traceback_file_path(frame))

class PathAPI:

    def __init__(self, file: str):
        self.file = file

    def __call__(self, anchor: str = None, frame: int = 1) -> Path:
        anchor = anchor if anchor else traceback_file_path(frame=frame)
        return inspect_module(anchor) / self.file
