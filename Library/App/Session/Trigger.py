from typing_extensions import Self
from dataclasses import dataclass

from Library.App.Session import StorageAPI

@dataclass(kw_only=True)
class TriggerAPI(StorageAPI):

    def trigger(self) -> Self:
        super().trigger()
        self.increment()
        return self
