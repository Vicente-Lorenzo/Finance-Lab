from pathlib import PurePath, Path
from sys import _getframe
from os import getcwd
from re import Pattern, compile, search
from dataclasses import dataclass, field

def inspect_file(file: str, header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    file: PurePath = builder("/") / file if header else builder(file)
    return file.resolve() if (isinstance(file, Path) and resolve) else file

def inspect_path(file: PurePath, footer: bool = False) -> str:
    sep: str = file._flavour.sep
    file: str = str(file)
    return file + sep if (footer and set(file) != set(sep)) else file

def inspect_file_path(file: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    path: PurePath = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=path, footer=footer)

def inspect_module(file: str, header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    path: PurePath = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return path.parent if path.suffix else path

def inspect_module_path(file: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    module: PurePath = inspect_module(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=module, footer=footer)

def traceback_working() -> str:
    return getcwd()

def traceback_working_module(header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    traceback: str = traceback_working()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_working_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_working()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth(depth: int = 1) -> str:
    f = _getframe(depth).f_code.co_filename
    return f if f not in ("<string>", "<stdin>", "<exec>") else None

def traceback_depth_file(header: bool = False, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> PurePath:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_file_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth_module(header: bool = False, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> PurePath:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_calling() -> str:
    depth: int = 0
    while (calling := traceback_depth(depth=depth)) is None or calling == __file__:
        depth += 1
    return calling if calling else traceback_working()

def traceback_calling_file(header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    traceback: str = traceback_calling()
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_file_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_calling_module(header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    traceback: str = traceback_calling()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_module_path(header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex(pattern: str) -> str:
    depth: int = 0
    pattern: Pattern = compile(pattern)
    while not search(pattern, calling := traceback_depth(depth=depth)):
        depth += 1
    return calling if calling else traceback_working()

def traceback_regex_file(pattern: str, header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_file_path(pattern: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex_module(pattern: str, header: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_module_path(pattern: str, header: bool = False, footer: bool = False, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

@dataclass(slots=True)
class PathAPI:

    File: str = field(init=True, repr=True)
    Module: PurePath = field(default=None, init=True, repr=True)

    def __post_init__(self):
        self.Module = self.Module or traceback_calling_module(resolve=True)

    @property
    def Path(self) -> PurePath:
        return self.Module / self.File
