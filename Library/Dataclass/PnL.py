import math
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

@dataclass(slots=True, kw_only=True)
class PnLAPI(DataclassAPI):
    PnL: float = field(init=True, repr=True)
    Reference: float = field(default=None, init=True, repr=True)

    @property
    def Return(self) -> float:
        return self.PnL / self.Reference
    @property
    def LogReturn(self) -> float:
        return math.log1p(self.Return)
