from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

@dataclass(kw_only=True)
class TriggerAPI(DataclassAPI):

    index: int = field(default=0, init=True, repr=True)

    def trigger(self) -> None:
        self.index += 1
