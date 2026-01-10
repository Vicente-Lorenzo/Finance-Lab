from dataclasses import dataclass, field
from Library.Dataclass import DataclassAPI

@dataclass(kw_only=True)
class LocationAPI(DataclassAPI):
    _index_: int = field(default=-1, init=True, repr=True)
    _stack_: list[str] = field(default_factory=list, init=True, repr=True)

    def current(self) -> str | None:
        if 0 <= self._index_ < len(self._stack_):
            return self._stack_[self._index_]
        return None

    def register(self, path: str) -> None:
        if self._index_ == -1:
            self._stack_ = [path]
            self._index_ = 0
            return
        if self.current() == path:
            return
        if self._index_ < len(self._stack_) - 1:
            self._stack_ = self._stack_[: self._index_ + 1]
        self._stack_.append(path)
        self._index_ = len(self._stack_) - 1

    def backward(self, *, step: bool = False) -> str | None:
        if self._index_ <= 0:
            return None
        if not step:
            return self._stack_[self._index_ - 1]
        self._index_ -= 1
        return self._stack_[self._index_]

    def forward(self, *, step: bool = False) -> str | None:
        if self._index_ < 0 or self._index_ >= len(self._stack_) - 1:
            return None
        if not step:
            return self._stack_[self._index_ + 1]
        self._index_ += 1
        return self._stack_[self._index_]
