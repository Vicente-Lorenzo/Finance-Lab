from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import PrimaryKey
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(slots=True, kw_only=True)
class CategoryAPI(DatapointAPI):

    Table: ClassVar[str] = "Category"

    UID: str | None = None
    Primary: str | None = None
    Secondary: str | None = None
    Alternative: str | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.UID: PrimaryKey(pl.String),
            cls.ID.Primary: pl.String(),
            cls.ID.Secondary: pl.String(),
            cls.ID.Alternative: pl.String(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if not self.UID and self.Primary and self.Secondary:
            self.UID = f"{self.Primary} ({self.Secondary})"
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self) -> None:
        if not self.UID and not self.Primary: return
            
        df = pl.DataFrame()
        if self.UID:
            escaped = self.UID.replace("'", "''")
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"UID\" = '{escaped}'", limit=1, legacy=False)
            if df.is_empty():
                df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Primary\" = '{escaped}' OR \"Secondary\" = '{escaped}' OR \"Alternative\" = '{escaped}'", limit=1, legacy=False)
                
        if df.is_empty() and self.Primary and self.Secondary:
            prim = self.Primary.replace("'", "''")
            sec = self.Secondary.replace("'", "''")
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Primary\" = '{prim}' AND \"Secondary\" = '{sec}'", limit=1, legacy=False)

        if df.is_empty():
            if self.Primary is None or self.Secondary is None:
                raise ValueError(f"Category '{self.UID or self.Primary}' not found in database and lacks required fields for creation.")
            return

        row = df.row(0, named=True)
        if not self.UID: self.UID = row.get("UID")
        if self.Primary is None: self.Primary = row.get("Primary")
        if self.Secondary is None: self.Secondary = row.get("Secondary")
        if self.Alternative is None: self.Alternative = row.get("Alternative")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=self.ID.UID)

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"CategoryAPI(UID={self.UID!r}, Primary={self.Primary!r}, Secondary={self.Secondary!r}, Alternative={self.Alternative!r})"