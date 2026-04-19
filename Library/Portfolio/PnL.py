from __future__ import annotations

import math
from dataclasses import dataclass, field

from Library.Database.Dataclass import DataclassAPI

@dataclass(slots=True, kw_only=True)
class PnLAPI(DataclassAPI):
    PnL: float = field(init=True, repr=True)
    Reference: float | None = field(default=None, init=True, repr=True)

    @property
    def Return(self) -> float | None:
        if not self.Reference: return None
        return self.PnL / self.Reference
    @property
    def LogReturn(self) -> float | None:
        ret = self.Return
        if ret is None or ret <= -1.0: return None
        return math.log1p(ret)