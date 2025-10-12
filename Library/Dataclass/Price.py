from __future__ import annotations

import math
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI
if TYPE_CHECKING: from Library.Dataclass import SymbolAPI

@dataclass(slots=True, kw_only=True)
class PriceAPI(DataclassAPI):
    Price: float = field(init=True, repr=True)
    Reference: float = field(default=None, init=True, repr=True)
    Symbol: SymbolAPI = field(default=None, init=True, repr=True)

    @property
    def Distance(self) -> float:
        return self.Price - self.Reference
    @property
    def Points(self) -> float:
        return self.Distance / self.Symbol.PointSize
    @property
    def Pips(self) -> float:
        return self.Distance / self.Symbol.PipSize
    @property
    def Percentage(self):
        return (self.Price / self.Reference) - 1.0
    @property
    def LogPercentage(self) -> float:
        return math.log1p(self.Percentage)
