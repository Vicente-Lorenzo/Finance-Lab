from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import Enumeration, as_enum
from Library.Database import PrimaryKey
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

class Provider(Enumeration):
    Spotware = 0
    Pepperstone = 1
    ICMarkets = 2
    Bloomberg = 3
    Yahoo = 4

class Platform(Enumeration):
    cTrader = 0
    MetaTrader4 = 1
    MetaTrader5 = 2
    NinjaTrader = 3
    QuantConnect = 4
    Web = 5
    API = 6

@dataclass(slots=True, kw_only=True)
class ProviderAPI(DatapointAPI):

    Table: ClassVar[str] = "Provider"

    UID: str | None = None
    Platform: Platform | str | None = None
    Name: str | None = None
    Abbreviation: str | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.UID: PrimaryKey(pl.String),
            cls.ID.Platform: pl.Enum([p.name for p in Platform]),
            cls.ID.Name: pl.String(),
            cls.ID.Abbreviation: pl.String(),
            **DatapointAPI.Structure()
        }

    @staticmethod
    def normalize(uid: str) -> str:
        return uid.replace("-", " ")

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        self.Platform = as_enum(Platform, self.Platform)
        if self.UID:
            self.UID = self.normalize(self.UID)
        elif self.Abbreviation and self.Platform:
            plat_name = self.Platform.name if isinstance(self.Platform, Enumeration) else self.Platform
            self.UID = f"{self.Abbreviation} ({plat_name})"
            
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self) -> None:
        if not self.UID and not self.Name and not self.Abbreviation: return
            
        df = pl.DataFrame()
        if self.UID:
            escaped_uid = self.UID.replace("'", "''")
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"UID\" = '{escaped_uid}'", limit=1, legacy=False)
            if df.is_empty():
                df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Name\" = '{escaped_uid}' OR \"Abbreviation\" = '{escaped_uid}'", limit=1, legacy=False)
                
        if df.is_empty() and self.Name:
            escaped_name = self.Name.replace("'", "''")
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Name\" = '{escaped_name}'", limit=1, legacy=False)

        if df.is_empty() and self.Abbreviation:
            escaped_abbr = self.Abbreviation.replace("'", "''")
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Abbreviation\" = '{escaped_abbr}'", limit=1, legacy=False)

        if df.is_empty():
            if self.Platform is None or self.Abbreviation is None:
                raise ValueError(f"Provider '{self.UID or self.Name or self.Abbreviation}' not found in database and lacks required fields for creation.")
            return
            
        row = df.row(0, named=True)
        if not self.UID: self.UID = row.get("UID")
        if self.Platform is None: self.Platform = as_enum(Platform, row.get("Platform"))
        if self.Name is None: self.Name = row.get("Name")
        if self.Abbreviation is None: self.Abbreviation = row.get("Abbreviation")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=self.ID.UID)

    def __str__(self) -> str:
        plat = f"-{self.Platform.name}" if isinstance(self.Platform, Enumeration) else (f"-{self.Platform}" if self.Platform else "")
        return f"{self.UID}{plat}" if self.UID else ""

    def __repr__(self) -> str:
        return f"ProviderAPI(UID={self.UID!r}, Platform={self.Platform!r}, Name={self.Name!r}, Abbreviation={self.Abbreviation!r})"