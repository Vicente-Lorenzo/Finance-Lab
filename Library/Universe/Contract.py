from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import Enumeration, as_enum
from Library.Database import ForeignKey
from Library.Universe.Ticker import TickerAPI
from Library.Universe.Provider import ProviderAPI
from Library.Utility.DateTime import Day
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING:
    from Library.Database import DatabaseAPI
    from Library.Market.Tick import TickAPI

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

@dataclass(slots=True, kw_only=True)
class ContractAPI(DatapointAPI):

    Table: ClassVar[str] = "Contract"

    TickerUID: str
    ProviderUID: str

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

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)
    _spot_tick_: TickAPI = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.TickerUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{TickerAPI.Table}"("{TickerAPI.ID.UID}")', primary=True),
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")', primary=True),
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
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        self.TickerUID = TickerAPI.normalize(self.TickerUID)
        self.ProviderUID = ProviderAPI.normalize(self.ProviderUID)
        self.CommissionMode = as_enum(CommissionMode, self.CommissionMode)
        self.SwapMode = as_enum(SwapMode, self.SwapMode)
        self.SwapExtraDay = as_enum(Day, self.SwapExtraDay)
        
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self) -> None:
        t = self.TickerUID.replace("'", "''")
        p = self.ProviderUID.replace("'", "''")
        df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"TickerUID\" = '{t}' AND \"ProviderUID\" = '{p}'", limit=1, legacy=False)
        if df.is_empty():
            return
            
        row = df.row(0, named=True)
        if self.Digits is None and row.get("Digits") is not None: self.Digits = row.get("Digits")
        if self.PointSize is None and row.get("PointSize") is not None: self.PointSize = row.get("PointSize")
        if self.PipSize is None and row.get("PipSize") is not None: self.PipSize = row.get("PipSize")
        if self.LotSize is None and row.get("LotSize") is not None: self.LotSize = row.get("LotSize")
        if self.VolumeMin is None and row.get("VolumeMin") is not None: self.VolumeMin = row.get("VolumeMin")
        if self.VolumeMax is None and row.get("VolumeMax") is not None: self.VolumeMax = row.get("VolumeMax")
        if self.VolumeStep is None and row.get("VolumeStep") is not None: self.VolumeStep = row.get("VolumeStep")
        if self.Commission is None and row.get("Commission") is not None: self.Commission = row.get("Commission")
        if self.CommissionMode is None: self.CommissionMode = as_enum(CommissionMode, row.get("CommissionMode"))
        if self.SwapLong is None and row.get("SwapLong") is not None: self.SwapLong = row.get("SwapLong")
        if self.SwapShort is None and row.get("SwapShort") is not None: self.SwapShort = row.get("SwapShort")
        if self.SwapMode is None: self.SwapMode = as_enum(SwapMode, row.get("SwapMode"))
        if self.SwapExtraDay is None: self.SwapExtraDay = as_enum(Day, row.get("SwapExtraDay"))
        if self.SwapSummerTime is None and row.get("SwapSummerTime") is not None: self.SwapSummerTime = row.get("SwapSummerTime")
        if self.SwapWinterTime is None and row.get("SwapWinterTime") is not None: self.SwapWinterTime = row.get("SwapWinterTime")
        if self.SwapPeriod is None and row.get("SwapPeriod") is not None: self.SwapPeriod = row.get("SwapPeriod")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=[self.ID.TickerUID, self.ID.ProviderUID])

    def __str__(self) -> str:
        return f"{self.TickerUID}@{self.ProviderUID}"