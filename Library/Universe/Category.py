from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import PrimaryKey
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(kw_only=True)
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
        if not self.UID and self.Primary and self.Secondary: self.UID = f"{self.Primary} ({self.Secondary})"
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self, condition: str | None = None) -> None:
        if condition:
            row = super().pull(condition=condition)
            if row:
                if not self.UID: self.UID = row.get("UID")
                if self.Primary is None: self.Primary = row.get("Primary")
                if self.Secondary is None: self.Secondary = row.get("Secondary")
                if self.Alternative is None: self.Alternative = row.get("Alternative")
            return
        if not self.UID and not self.Primary: return
        row = None
        if self.UID:
            escaped = self.UID.replace("'", "''")
            row = super().pull(condition=f"\"UID\" = '{escaped}'")
            if not row: row = super().pull(condition=f"\"Primary\" = '{escaped}' OR \"Secondary\" = '{escaped}' OR \"Alternative\" = '{escaped}'")
        if not row and self.Primary and self.Secondary:
            prim = self.Primary.replace("'", "''")
            sec = self.Secondary.replace("'", "''")
            row = super().pull(condition=f"\"Primary\" = '{prim}' AND \"Secondary\" = '{sec}'")
        if not row:
            if self.Primary is None or self.Secondary is None: raise ValueError(f"Category '{self.UID or self.Primary}' not found in database and lacks required fields for creation.")
            return
        if not self.UID: self.UID = row.get("UID")
        if self.Primary is None: self.Primary = row.get("Primary")
        if self.Secondary is None: self.Secondary = row.get("Secondary")
        if self.Alternative is None: self.Alternative = row.get("Alternative")

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.UID)

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"CategoryAPI(UID={self.UID!r}, Primary={self.Primary!r}, Secondary={self.Secondary!r}, Alternative={self.Alternative!r})"