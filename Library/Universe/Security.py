from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import ForeignKey
from Library.Universe.Ticker import TickerAPI
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Contract import ContractAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(slots=True, kw_only=True)
class SecurityAPI(DatapointAPI):

    Table: ClassVar[str] = "Security"

    ProviderUID: str
    CategoryUID: str | None = None
    TickerUID: str

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")', primary=True),
            cls.ID.CategoryUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{CategoryAPI.Table}"("{CategoryAPI.ID.UID}")', primary=True),
            cls.ID.TickerUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{TickerAPI.Table}"("{TickerAPI.ID.UID}")', primary=True),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        self.TickerUID = TickerAPI.normalize(self.TickerUID)
        self.ProviderUID = ProviderAPI.normalize(self.ProviderUID)
        self._db_ = self._connect_(db)
        
        if not self.CategoryUID:
            t = TickerAPI(UID=self.TickerUID, db=self._db_)
            self.CategoryUID = t.Category or ""
            
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self) -> None:
        p = self.ProviderUID.replace("'", "''")
        c = self.CategoryUID.replace("'", "''")
        t = self.TickerUID.replace("'", "''")
        df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"ProviderUID\" = '{p}' AND \"CategoryUID\" = '{c}' AND \"TickerUID\" = '{t}'", limit=1, legacy=False)
        if df.is_empty():
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"ProviderUID\" = '{p}' AND \"TickerUID\" = '{t}'", limit=1, legacy=False)
            
        if df.is_empty():
            if not self.CategoryUID:
                raise ValueError(f"Security '{self.TickerUID}@{self.ProviderUID}' not found in database.")
            return
            
        row = df.row(0, named=True)
        if not self.CategoryUID: self.CategoryUID = row.get("CategoryUID")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        self.Ticker.push(by=by)
        self.Provider.push(by=by)
        if self.CategoryUID:
            self.Category.push(by=by)
        self.Contract.push(by=by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=[self.ID.ProviderUID, self.ID.CategoryUID, self.ID.TickerUID])

    @property
    def Ticker(self) -> TickerAPI:
        return TickerAPI(UID=self.TickerUID, db=self._db_)

    @property
    def Provider(self) -> ProviderAPI:
        return ProviderAPI(UID=self.ProviderUID, db=self._db_)

    @property
    def Contract(self) -> ContractAPI:
        return ContractAPI(TickerUID=self.TickerUID, ProviderUID=self.ProviderUID, db=self._db_)

    @property
    def Category(self) -> CategoryAPI:
        return CategoryAPI(UID=self.CategoryUID, db=self._db_)

    def __str__(self) -> str:
        return f"{self.TickerUID}@{self.ProviderUID}"

    def __repr__(self) -> str:
        return f"SecurityAPI(ProviderUID={self.ProviderUID!r}, CategoryUID={self.CategoryUID!r}, TickerUID={self.TickerUID!r})"