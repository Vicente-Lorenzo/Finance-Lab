from pathlib import Path
from sys import _getframe
from os import sep, getcwd
from re import Pattern, compile, search
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

def traceback_working() -> str:
    return getcwd()

def traceback_working_module(header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_working()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_working_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_working()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth(depth: int = 1) -> str:
    f = _getframe(depth).f_code.co_filename
    return f if f not in ("<string>", "<stdin>", "<exec>") else None

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

def traceback_calling() -> str:
    depth: int = 0
    while (calling := traceback_depth(depth=depth)) is None or calling == __file__:
        depth += 1
    return calling if calling else traceback_working()

def traceback_calling_file(header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_calling()
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_file_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_calling_module(header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_calling()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex(pattern: str) -> str:
    depth: int = 0
    pattern: Pattern = compile(pattern)
    while not search(pattern, calling := traceback_depth(depth=depth)):
        depth += 1
    return calling if calling else traceback_working()

def traceback_regex_file(pattern: str, header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_file_path(pattern: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex_module(pattern: str, header: bool = False, resolve: bool = False, builder: type[Path] = Path) -> Path:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_module_path(pattern: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[Path] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

@dataclass(slots=True)
class PathAPI:

    File: str = field(init=True, repr=True)
    Module: Path = field(default=None, init=True, repr=True)

    def __post_init__(self):
        self.Module = self.Module or traceback_calling_module(resolve=True)

    @property
    def Path(self) -> Path:
        return self.Module / self.File
