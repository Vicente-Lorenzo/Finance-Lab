from dataclasses import dataclass, field
from Library.Dataclass import DataclassAPI

@dataclass(slots=True)
class TerminalSessionAPI(DataclassAPI):

    Buffer: str = field(default="", init=True, repr=True)
    MaxLength: int = field(default=20000, init=True, repr=True)

    def Add(self, text: str) -> None:
        if not text:
            return
        self.Buffer += text
        if len(self.Buffer) > self.MaxLength:
            self.Buffer = self.Buffer[-self.MaxLength:]

    def Clear(self) -> None:
        self.Buffer = ""
