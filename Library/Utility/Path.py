from os import getcwd
from sys import _getframe
from pathlib import PurePath, Path
from re import Pattern, compile, search

from Library.Utility import contains, is_notebook, find_notebook

def inspect_separator(builder: type[PurePath] = Path) -> str:
    return builder(".")._flavour.sep

def inspect_file(file: PurePath | str | None, *, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    sep: str = inspect_separator(builder=builder)
    file: str = str(file) if file else ""
    if header is True:
        file: PurePath = builder(sep) / builder(file)
    elif header is False:
        file: PurePath = builder(file.lstrip(sep))
    else:
        file: PurePath = builder(file)
    return file.resolve() if (isinstance(file, Path) and resolve) else file

def inspect_path(file: PurePath, *, footer: bool = None) -> str:
    sep: str = inspect_separator(builder=type(file))
    file: str = str(file)
    if footer is True:
        return file + sep if set(file) != set(sep) else file
    elif footer is False:
        return file.rstrip(sep)
    else:
        return file

def inspect_file_path(file: PurePath | str | None, *, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    path: PurePath = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=path, footer=footer)

def inspect_module(file: PurePath | str | None, *, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    path: PurePath = inspect_file(file=file, header=header, resolve=resolve, builder=builder)
    return path.parent if path.suffix else path

def inspect_module_path(file: str | None, *, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    module: PurePath = inspect_module(file=file, header=header, resolve=resolve, builder=builder)
    return inspect_path(file=module, footer=footer)

def traceback_working() -> str:
    return getcwd()

def traceback_working_module(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_working()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_working_module_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_working()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth(*, depth: int = 1) -> str | None:
    f: str = _getframe(depth).f_code.co_filename
    if f.startswith("<") and f.endswith(">"):
        return find_notebook() if is_notebook() else traceback_working()
    if contains(f, ("ipython", "ipykernel", "interactiveshell", "runpy")):
        return find_notebook() if is_notebook() else f
    return f

def traceback_depth_file(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> PurePath | Path:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_file_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_depth_module(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> PurePath | Path:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_depth_module_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path, depth: int = 2) -> str:
    traceback: str = traceback_depth(depth=depth)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_origin() -> str:
    depth: int = 0
    origin: str | None = None
    try:
        while origin := traceback_depth(depth=depth):
            depth += 1
    except ValueError:
        depth -= 1
        origin = traceback_depth(depth=depth)
    finally:
        return origin

def traceback_origin_file(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_origin()
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_origin_file_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_origin()
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_origin_module(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_origin()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_origin_module_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_origin()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_current():
    depth: int = 0
    while current := traceback_depth(depth=depth):
        if current != __file__: break
        depth += 1
    return current

def traceback_current_file(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_current()
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_current_file_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_current()
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_current_module(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_current()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_current_module_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_current()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_calling() -> str:
    depth: int = 0
    current: str = traceback_current()
    while calling := traceback_depth(depth=depth):
        if calling != __file__ and calling != current: break
        depth += 1
    return calling

def traceback_calling_file(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_calling()
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_file_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_calling_module(*, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_calling()
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_calling_module_path(*, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_calling()
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex(*, pattern: str) -> str:
    depth: int = 0
    pattern: Pattern = compile(pattern)
    while not search(pattern, expression := traceback_depth(depth=depth)):
        depth += 1
    return expression

def traceback_regex_file(pattern: str, *, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_file_path(pattern: str, *, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_file_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

def traceback_regex_module(pattern: str, *, header: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> PurePath | Path:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module(file=traceback, header=header, resolve=resolve, builder=builder)

def traceback_regex_module_path(pattern: str, *, header: bool = None, footer: bool = None, resolve: bool = False, builder: type[PurePath] = Path) -> str:
    traceback: str = traceback_regex(pattern=pattern)
    return inspect_module_path(file=traceback, header=header, footer=footer, resolve=resolve, builder=builder)

class PathAPI:

    def __init__(self, path: str | Path, module: str | Path = None):
        if isinstance(path, str):
            self.path: str = path
        else:
            self.path: str = inspect_path(path)
        if module is None:
            self.module: Path = traceback_current_module(resolve=True)
        elif isinstance(module, str):
            self.module: Path = inspect_module(module, resolve=True)
        else:
            self.module: Path = module

    @property
    def file(self) -> Path:
        return self.module / self.path

    def __repr__(self):
        return inspect_path(self.file)
