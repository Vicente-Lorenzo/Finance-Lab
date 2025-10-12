from enum import Enum
from typing import Callable
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

class IndicatorType(Enum):
    Baseline = 0
    Overlap = 1
    Momentum = 2
    Volume = 3
    Volatility = 4
    Pattern = 5
    Other = 6

class IndicatorMode(Enum):
    Off = 0
    Filter = 1
    Signal = 2

@dataclass(slots=True, kw_only=True)
class IndicatorConfigurationAPI(DataclassAPI):
    Name: str = field(init=True, repr=True)
    IndicatorType: IndicatorType = field(init=True, repr=True)
    Input: Callable = field(init=True, repr=True)
    Parameters: dict[str, list[list[int | float]]] = field(init=True, repr=True)
    Constraints: Callable = field(init=True, repr=True)
    Function: Callable = field(init=True, repr=True)
    Output: list[str] = field(init=True, repr=True)
    FilterBuy: Callable = field(init=True, repr=True)
    FilterSell: Callable = field(init=True, repr=True)
    SignalBuy: Callable = field(init=True, repr=True)
    SignalSell: Callable = field(init=True, repr=True)

    def __post_init__(self):
        self.IndicatorType = IndicatorType(self.IndicatorType)
