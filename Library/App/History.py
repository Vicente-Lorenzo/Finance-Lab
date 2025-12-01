from dataclasses import dataclass, field
from Library.Dataclass import DataclassAPI

@dataclass(slots=True)
class HistorySessionAPI(DataclassAPI):

    Index: int = field(default=-1, init=True, repr=True)
    Stack: list = field(default_factory=list, init=True, repr=True)

    def register(self, path: str) -> None:
        if self.Index == -1 or (self.Index >= 0 and self.Stack[self.Index] != path):
            self.Stack = self.Stack[:self.Index + 1]
            self.Stack.append(path)
            self.Index = len(self.Stack) - 1

    def backward(self) -> int | None:
        if self.Index > 0:
            return self.Stack[self.Index - 1]
        return None

    def forward(self) -> int | None:
        if self.Index < len(self.Stack) - 1:
            return self.Stack[self.Index + 1]
        return None
