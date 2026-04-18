from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass

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

    def _apply_(self, row: dict) -> None:
        if not self.UID: self.UID = row.get("UID")
        if self.Primary is None: self.Primary = row.get("Primary")
        if self.Secondary is None: self.Secondary = row.get("Secondary")
        if self.Alternative is None: self.Alternative = row.get("Alternative")

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.UID and not self.Primary: return
        row = None
        if self.UID:
            row = super().pull(
                condition='"UID" = :value: OR "Primary" = :value: OR "Secondary" = :value: OR "Alternative" = :value:',
                parameters={"value": self.UID}
            )
        if not row and self.Primary and self.Secondary:
            row = super().pull(
                condition='"Primary" = :primary: AND "Secondary" = :secondary:',
                parameters={"primary": self.Primary, "secondary": self.Secondary}
            )
        if not row:
            if self.Primary is None or self.Secondary is None: raise ValueError(f"Category '{self.UID or self.Primary}' not found in database and lacks required fields for creation.")
            return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.UID)

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"CategoryAPI(UID={self.UID!r}, Primary={self.Primary!r}, Secondary={self.Secondary!r}, Alternative={self.Alternative!r})"