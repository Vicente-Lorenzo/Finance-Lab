from sys import _getframe
from pathlib import Path
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

def inspect_file(file: str | Path) -> Path:
    return Path(file).resolve()

def inspect_file_path(file: str | Path) -> str:
    return str(inspect_file(file))

def inspect_module(file: str | Path) -> Path:
    return inspect_file(file).parent

def inspect_module_path(file: str | Path) -> str:
    return inspect_file_path(inspect_module(file))

def traceback_file(frame: int = None) -> Path:
    return inspect_file(traceback_file_path(frame))

def traceback_file_path(frame: int = None) -> str:
    return _getframe(frame if frame is not None else 3).f_code.co_filename

def traceback_module(frame: int = None) -> Path:
    return inspect_module(traceback_file_path(frame))

def traceback_module_path(frame: int = None) -> str:
    return inspect_module_path(traceback_file_path(frame))

@dataclass(slots=True)
class PathAPI(DataclassAPI):

    File: str = field(init=True, repr=True)
    Anchor: str = field(default=None, init=True, repr=True)

    Module: Path = field(init=False, repr=True)
    Path: Path = field(init=False, repr=True)

    def __post_init__(self):
        self.Anchor = self.Anchor if self.Anchor is not None else traceback_file_path()
        self.Module = inspect_module(self.Anchor)
        self.Path = self.Module / self.File
