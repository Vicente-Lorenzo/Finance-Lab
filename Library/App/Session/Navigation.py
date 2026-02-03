from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

@dataclass(kw_only=True)
class NavigationAPI(DataclassAPI):

    index: int = field(default=0, init=True, repr=True)
    href: str | None = field(default=None, init=True, repr=True)
    external: bool = field(default=False, init=True, repr=True)
    replace: bool = field(default=False, init=True, repr=True)

    def clear(self) -> None:
        self.href = None
        self.external = False
        self.replace = False

    def redirect(self, href: str, *, external: bool = False) -> None:
        self.index += 1
        self.href = href
        self.external = external
