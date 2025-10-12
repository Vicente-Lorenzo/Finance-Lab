from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI, AssetType
if TYPE_CHECKING: from Library.Dataclass import TickAPI

class SpreadType(Enum):
    Points = 0
    Percentage = 1
    Random = 2
    Approximate = 3
    Accurate = 4

class CommissionType(Enum):
    Points = 0
    Percentage = 1
    Amount = 2
    Accurate = 3

class CommissionMode(Enum):
    BaseAssetPerMillionVolume = 0
    BaseAssetPerOneLot = 1
    PercentageOfVolume = 2
    QuoteAssetPerOneLot = 3

class SwapType(Enum):
    Points = 0
    Percentage = 1
    Amount = 2
    Accurate = 3

class SwapMode(Enum):
    Pips = 0
    Percentage = 1

class DayOfWeek(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

@dataclass(slots=True, kw_only=True)
class SymbolAPI(DataclassAPI):
    BaseAssetType: AssetType = field(init=True, repr=True)
    QuoteAssetType: AssetType = field(init=True, repr=True)
    Digits: int = field(init=True, repr=True)
    PointSize: float = field(init=True, repr=True)
    PipSize: float = field(init=True, repr=True)
    LotSize: int = field(init=True, repr=True)
    VolumeMin: float = field(init=True, repr=True)
    VolumeMax: float = field(init=True, repr=True)
    VolumeStep: float = field(init=True, repr=True)
    Commission: float = field(init=True, repr=True)
    CommissionMode: CommissionMode = field(init=True, repr=True)
    SwapLong: float = field(init=True, repr=True)
    SwapShort: float = field(init=True, repr=True)
    SwapMode: SwapMode = field(init=True, repr=True)
    SwapExtraDay: DayOfWeek = field(init=True, repr=True)
    SwapSummerTime: int = field(default=22, init=True, repr=True)
    SwapWinterTime: int = field(default=21, init=True, repr=True)
    SwapPeriod: int = field(default=24, init=True, repr=True)

    _SpotTick: TickAPI = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

    @property
    def AskUnitValue(self) -> float:
        return 1.0 * self._SpotTick.AskBaseConversion
    @property
    def BidUnitValue(self) -> float:
        return 1.0 * self._SpotTick.BidBaseConversion
    @property
    def AskLotValue(self) -> float:
        return self.LotSize * self._SpotTick.AskBaseConversion
    @property
    def BidLotValue(self) -> float:
        return self.LotSize * self._SpotTick.BidBaseConversion

    @property
    def AskPointValue(self) -> float:
        return self.PointSize * self.LotSize * self._SpotTick.AskQuoteConversion
    @property
    def BidPointValue(self) -> float:
        return self.PointSize * self.LotSize * self._SpotTick.BidQuoteConversion
    @property
    def AskPipValue(self) -> float:
        return self.PipSize * self.LotSize * self._SpotTick.AskQuoteConversion
    @property
    def BidPipValue(self) -> float:
        return self.PipSize * self.LotSize * self._SpotTick.BidQuoteConversion

    @property
    def SpotTick(self) -> TickAPI:
        return self._SpotTick
    @SpotTick.setter
    def SpotTick(self, spot_tick: TickAPI):
        self._SpotTick = spot_tick
