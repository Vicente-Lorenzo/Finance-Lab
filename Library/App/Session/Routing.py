from typing_extensions import Self
from dataclasses import dataclass, field

from Library.App.Session import StorageAPI

@dataclass(kw_only=True)
class RoutingAPI(StorageAPI):

    href: str | None = field(default=None, init=True, repr=True)
    external: bool = field(default=False, init=True, repr=True)
    replace: bool = field(default=False, init=True, repr=True)

    def redirect(self, href: str, *, external: bool = False) -> Self:
        self.trigger()
        self.href = href
        self.external = external
        return self

    def clear(self) -> Self:
        self.href = None
        self.external = False
        self.replace = False
        return self
