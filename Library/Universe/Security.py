from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import as_enum
from Library.Database.Database import PrimaryKey, ForeignKey
from Library.Universe.Ticker import TickerAPI, Instrument
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Contract import ContractAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(kw_only=True)
class SecurityAPI(DatapointAPI):

    Table: ClassVar[str] = "Security"

    ProviderUID: str
    CategoryUID: str | None = None
    TickerUID: str
    Instrument: Instrument | str | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")', primary=True),
            cls.ID.CategoryUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{CategoryAPI.Table}"("{CategoryAPI.ID.UID}")', primary=True),
            cls.ID.TickerUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{TickerAPI.Table}"("{TickerAPI.ID.UID}")', primary=True),
            cls.ID.Instrument: PrimaryKey(pl.Enum([i.name for i in Instrument])),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if not self.Instrument: self.Instrument = TickerAPI.detect(self.TickerUID)
        self.Instrument = as_enum(Instrument, self.Instrument)
        self.TickerUID = TickerAPI.normalize(self.TickerUID)
        self.ProviderUID = ProviderAPI.normalize(self.ProviderUID)
        self._db_ = self._connect_(db)
        if not self.CategoryUID:
            t = TickerAPI(UID=self.TickerUID, db=self._db_)
            self.CategoryUID = t.Category or ""
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self, condition: str | None = None) -> None:
        if condition:
            row = super().pull(condition=condition)
            if row:
                if not self.CategoryUID: self.CategoryUID = row.get("CategoryUID")
                if not self.Instrument: self.Instrument = as_enum(Instrument, row.get("Instrument"))
            return
        p = self.ProviderUID.replace("'", "''")
        c = (self.CategoryUID or "").replace("'", "''")
        t = self.TickerUID.replace("'", "''")
        inst = self.Instrument.name if isinstance(self.Instrument, Instrument) else self.Instrument
        row = super().pull(condition=f"\"ProviderUID\" = '{p}' AND \"CategoryUID\" = '{c}' AND \"TickerUID\" = '{t}' AND \"Instrument\" = '{inst}'")
        if not row: row = super().pull(condition=f"\"ProviderUID\" = '{p}' AND \"TickerUID\" = '{t}' AND \"Instrument\" = '{inst}'")
        if not row:
            if not self.CategoryUID: raise ValueError(f"Security '{self.TickerUID}@{self.ProviderUID}' not found in database.")
            return
        if not self.CategoryUID: self.CategoryUID = row.get("CategoryUID")
        if not self.Instrument: self.Instrument = as_enum(Instrument, row.get("Instrument"))

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        self.Ticker.push(by=by)
        self.Provider.push(by=by)
        if self.CategoryUID: self.Category.push(by=by)
        self.Contract.push(by=by)
        super().push(by=by, key=key or [self.ID.ProviderUID, self.ID.CategoryUID, self.ID.TickerUID, self.ID.Instrument])

    @property
    def Ticker(self) -> TickerAPI:
        return TickerAPI(UID=self.TickerUID, db=self._db_)

    @property
    def Provider(self) -> ProviderAPI:
        return ProviderAPI(UID=self.ProviderUID, db=self._db_)

    @property
    def Contract(self) -> ContractAPI:
        return ContractAPI(TickerUID=self.TickerUID, ProviderUID=self.ProviderUID, Instrument=self.Instrument, db=self._db_)

    @property
    def Category(self) -> CategoryAPI:
        return CategoryAPI(UID=self.CategoryUID, db=self._db_)

    def __str__(self) -> str:
        return f"{self.TickerUID}@{self.ProviderUID}"

    def __repr__(self) -> str:
        return f"SecurityAPI(ProviderUID={self.ProviderUID!r}, CategoryUID={self.CategoryUID!r}, TickerUID={self.TickerUID!r})"