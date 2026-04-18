from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass

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

@dataclass(kw_only=True)
class ProviderAPI(DatapointAPI):

    Table: ClassVar[str] = "Provider"

    UID: str | None = None
    Platform: Platform | str | None = None
    Name: str | None = None
    Abbreviation: str | None = None

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
        if self.UID: self.UID = self.normalize(self.UID)
        elif self.Abbreviation and self.Platform:
            self.UID = f"{self.Abbreviation} ({self.Platform.name})"
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _apply_(self, row: dict) -> None:
        if not self.UID: self.UID = row.get("UID")
        if self.Platform is None: self.Platform = as_enum(Platform, row.get("Platform"))
        if self.Name is None: self.Name = row.get("Name")
        if self.Abbreviation is None: self.Abbreviation = row.get("Abbreviation")

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.UID and not self.Name and not self.Abbreviation: return
        clauses = []
        params = {}
        if self.UID:
            clauses.append('"UID" = :uid:')
            params["uid"] = self.UID
        if self.Name:
            clauses.append('"Name" = :name:')
            params["name"] = self.Name
        if self.Abbreviation:
            clauses.append('"Abbreviation" = :abbr:')
            params["abbr"] = self.Abbreviation
        row = super().pull(condition=" OR ".join(clauses), parameters=params)
        if not row:
            if self.Platform is None or self.Abbreviation is None: raise ValueError(f"Provider '{self.UID or self.Name or self.Abbreviation}' not found in database and lacks required fields for creation.")
            return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.UID)

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"ProviderAPI(UID={self.UID!r}, Platform={self.Platform!r}, Name={self.Name!r}, Abbreviation={self.Abbreviation!r})"