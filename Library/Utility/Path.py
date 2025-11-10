from pathlib import Path
from os import sep, getcwd
from sys import _getframe
from dataclasses import dataclass, field

def inspect_file(file: str | Path, header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    file: Path = builder("/") / file if header else builder(file)
    return file.resolve() if resolve else file

def inspect_path(file: Path, footer: bool = False) -> str:
    return f"{file}{sep}" if footer else f"{file}"

def inspect_file_path(file: str | Path, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    path: Path = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=path, footer=footer)

def inspect_module(file: str | Path, header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    path: Path = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return path.parent if path.suffix else path

def inspect_module_path(file: str | Path, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    module: Path = inspect_module(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=module, footer=footer)

def traceback_depth(depth: int = 1) -> str:
    return _getframe(depth).f_code.co_filename

def traceback_depth_file(header: bool = False, resolve: bool = False, builder: type[Path] = Path, depth: int = 2) -> Path:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_file_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth_module(header: bool = False, resolve: bool = False, builder: type[Path] = Path, depth: int = 2) -> Path:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_working() -> str:
    return getcwd()

def traceback_working_module(header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_working()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_working_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_working()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

@dataclass(slots=True)
class PathAPI:
    File: str = field(init=True, repr=True)
    Module: Path = field(default=None, init=True, repr=True)

    def __post_init__(self):
        self.Module = self.Module or traceback_working_module()

    @property
    def Path(self) -> Path:
        return self.Module / self.File
