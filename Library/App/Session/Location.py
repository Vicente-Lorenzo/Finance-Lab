from dataclasses import dataclass, field
from Library.Dataclass import DataclassAPI

@dataclass(kw_only=True)
class LocationAPI(DataclassAPI):

    index: int = field(default=-1, init=True, repr=True)
    stack: list[str] = field(default_factory=list, init=True, repr=True)

    def current(self) -> str | None:
        if 0 <= self.index < len(self.stack):
            return self.stack[self.index]
        return None

    def register(self, path: str) -> None:
        if self.index == -1:
            self.stack = [path]
            self.index = 0
            return
        if self.current() == path:
            return
        if self.index < len(self.stack) - 1:
            self.stack = self.stack[: self.index + 1]
        self.stack.append(path)
        self.index = len(self.stack) - 1

    def backward(self, *, step: bool = False) -> str | None:
        if self.index <= 0:
            return None
        if not step:
            return self.stack[self.index - 1]
        self.index -= 1
        return self.stack[self.index]

    def forward(self, *, step: bool = False) -> str | None:
        if self.index < 0 or self.index >= len(self.stack) - 1:
            return None
        if not step:
            return self.stack[self.index + 1]
        self.index += 1
        return self.stack[self.index]
