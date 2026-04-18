from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import Enumeration, as_enum
from Library.Database import PrimaryKey, ForeignKey
from Library.Universe.Ticker import TickerAPI, Instrument
from Library.Universe.Provider import ProviderAPI
from Library.Utility.DateTime import Day
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING:
    from Library.Database import DatabaseAPI

class SpreadType(Enumeration):
    Points = 0
    Percentage = 1
    Random = 2
    Approximate = 3
    Accurate = 4

class CommissionType(Enumeration):
    Points = 0
    Percentage = 1
    Amount = 2
    Accurate = 3

class CommissionMode(Enumeration):
    BaseAssetPerMillionVolume = 0
    BaseAssetPerOneLot = 1
    PercentageOfVolume = 2
    QuoteAssetPerOneLot = 3

class SwapType(Enumeration):
    Points = 0
    Percentage = 1
    Amount = 2
    Accurate = 3

class SwapMode(Enumeration):
    Pips = 0
    Percentage = 1

@dataclass(kw_only=True)
class ContractAPI(DatapointAPI):

    Table: ClassVar[str] = "Contract"

    TickerUID: str
    ProviderUID: str
    Instrument: Instrument | str | None = None

    Digits: int | None = None
    PointSize: float | None = None
    PipSize: float | None = None
    LotSize: int | None = None
    VolumeMin: float | None = None
    VolumeMax: float | None = None
    VolumeStep: float | None = None
    Commission: float | None = None
    CommissionMode: CommissionMode | str | None = None
    SwapLong: float | None = None
    SwapShort: float | None = None
    SwapMode: SwapMode | str | None = None
    SwapExtraDay: Day | str | None = None
    SwapSummerTime: int = 22
    SwapWinterTime: int = 21
    SwapPeriod: int = 24
    Expiry: datetime | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.TickerUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{TickerAPI.Table}"("{TickerAPI.ID.UID}")', primary=True),
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")', primary=True),
            cls.ID.Instrument: PrimaryKey(pl.Enum([i.name for i in Instrument])),
            cls.ID.Digits: pl.Int32(),
            cls.ID.PointSize: pl.Float64(),
            cls.ID.PipSize: pl.Float64(),
            cls.ID.LotSize: pl.Int32(),
            cls.ID.VolumeMin: pl.Float64(),
            cls.ID.VolumeMax: pl.Float64(),
            cls.ID.VolumeStep: pl.Float64(),
            cls.ID.Commission: pl.Float64(),
            cls.ID.CommissionMode: pl.Enum([c.name for c in CommissionMode]),
            cls.ID.SwapLong: pl.Float64(),
            cls.ID.SwapShort: pl.Float64(),
            cls.ID.SwapMode: pl.Enum([s.name for s in SwapMode]),
            cls.ID.SwapExtraDay: pl.Enum([d.name for d in Day]),
            cls.ID.SwapSummerTime: pl.Int32(),
            cls.ID.SwapWinterTime: pl.Int32(),
            cls.ID.SwapPeriod: pl.Int32(),
            cls.ID.Expiry: pl.Datetime(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        self.TickerUID = TickerAPI.normalize(self.TickerUID)
        self.ProviderUID = ProviderAPI.normalize(self.ProviderUID)
        self.Instrument = as_enum(Instrument, self.Instrument)
        self.CommissionMode = as_enum(CommissionMode, self.CommissionMode)
        self.SwapMode = as_enum(SwapMode, self.SwapMode)
        self.SwapExtraDay = as_enum(Day, self.SwapExtraDay)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self, condition: str | None = None) -> None:
        if condition:
            row = super().pull(condition=condition)
            if row:
                if self.Digits is None: self.Digits = row.get("Digits")
                if self.PointSize is None: self.PointSize = row.get("PointSize")
                if self.PipSize is None: self.PipSize = row.get("PipSize")
                if self.LotSize is None: self.LotSize = row.get("LotSize")
                if self.VolumeMin is None: self.VolumeMin = row.get("VolumeMin")
                if self.VolumeMax is None: self.VolumeMax = row.get("VolumeMax")
                if self.VolumeStep is None: self.VolumeStep = row.get("VolumeStep")
                if self.Commission is None: self.Commission = row.get("Commission")
                if self.CommissionMode is None: self.CommissionMode = as_enum(CommissionMode, row.get("CommissionMode"))
                if self.SwapLong is None: self.SwapLong = row.get("SwapLong")
                if self.SwapShort is None: self.SwapShort = row.get("SwapShort")
                if self.SwapMode is None: self.SwapMode = as_enum(SwapMode, row.get("SwapMode"))
                if self.SwapExtraDay is None: self.SwapExtraDay = as_enum(Day, row.get("SwapExtraDay"))
                if self.SwapSummerTime is None: self.SwapSummerTime = row.get("SwapSummerTime")
                if self.SwapWinterTime is None: self.SwapWinterTime = row.get("SwapWinterTime")
                if self.SwapPeriod is None: self.SwapPeriod = row.get("SwapPeriod")
                if self.Expiry is None: self.Expiry = row.get("Expiry")
            return
        t = self.TickerUID.replace("'", "''")
        p = self.ProviderUID.replace("'", "''")
        inst = self.Instrument.name if isinstance(self.Instrument, Instrument) else self.Instrument
        row = super().pull(condition=f"\"TickerUID\" = '{t}' AND \"ProviderUID\" = '{p}' AND \"Instrument\" = '{inst}'")
        if not row: return
        if self.Digits is None: self.Digits = row.get("Digits")
        if self.PointSize is None: self.PointSize = row.get("PointSize")
        if self.PipSize is None: self.PipSize = row.get("PipSize")
        if self.LotSize is None: self.LotSize = row.get("LotSize")
        if self.VolumeMin is None: self.VolumeMin = row.get("VolumeMin")
        if self.VolumeMax is None: self.VolumeMax = row.get("VolumeMax")
        if self.VolumeStep is None: self.VolumeStep = row.get("VolumeStep")
        if self.Commission is None: self.Commission = row.get("Commission")
        if self.CommissionMode is None: self.CommissionMode = as_enum(CommissionMode, row.get("CommissionMode"))
        if self.SwapLong is None: self.SwapLong = row.get("SwapLong")
        if self.SwapShort is None: self.SwapShort = row.get("SwapShort")
        if self.SwapMode is None: self.SwapMode = as_enum(SwapMode, row.get("SwapMode"))
        if self.SwapExtraDay is None: self.SwapExtraDay = as_enum(Day, row.get("SwapExtraDay"))
        if self.SwapSummerTime is None: self.SwapSummerTime = row.get("SwapSummerTime")
        if self.SwapWinterTime is None: self.SwapWinterTime = row.get("SwapWinterTime")
        if self.SwapPeriod is None: self.SwapPeriod = row.get("SwapPeriod")
        if self.Expiry is None: self.Expiry = row.get("Expiry")

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or [self.ID.TickerUID, self.ID.ProviderUID, self.ID.Instrument])

    def __str__(self) -> str:
        return f"{self.TickerUID}@{self.ProviderUID}"