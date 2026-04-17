from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING, Sequence
from dataclasses import dataclass, field, InitVar
from datetime import datetime

from Library.Database.Dataframe import pl
from Library.Database.Dataclass import DataclassAPI
if TYPE_CHECKING: from Library.Database.Database import DatabaseAPI

@dataclass(kw_only=True)
class DatapointAPI(DataclassAPI):

    Database: ClassVar[str] = "Quant"
    Schema: ClassVar[str] = "Universe"
    Table: ClassVar[str] = "Datapoint"

    CreatedAt: datetime | None = None
    CreatedBy: str | None = None
    UpdatedAt: datetime | None = None
    UpdatedBy: str | None = None

    db: InitVar[DatabaseAPI | None] = None
    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        pass

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.CreatedAt: pl.Datetime(),
            cls.ID.CreatedBy: pl.String(),
            cls.ID.UpdatedAt: pl.Datetime(),
            cls.ID.UpdatedBy: pl.String()
        }

    def _audit_(self, actor: str) -> None:
        now = datetime.now()
        if self.CreatedBy is None:
            self.CreatedBy = actor
            self.CreatedAt = now
        self.UpdatedBy = actor
        self.UpdatedAt = now

    def _pull_audit_(self, row: dict) -> None:
        if self.CreatedBy is None: self.CreatedBy = row.get("CreatedBy")
        if self.UpdatedBy is None: self.UpdatedBy = row.get("UpdatedBy")
        if self.CreatedAt is None: self.CreatedAt = row.get("CreatedAt")
        if self.UpdatedAt is None: self.UpdatedAt = row.get("UpdatedAt")

    def _connect_(self, db: DatabaseAPI | None) -> DatabaseAPI:
        if db is None:
            from Library.Database.Postgres.Postgres import PostgresDatabaseAPI
            db = PostgresDatabaseAPI(database=self.Database).connect()
        return db

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=self.Schema, table=self.Table, data=clean_data, key=key, exclude=["CreatedAt", "CreatedBy"])

    def pull(self, condition: str | None = None) -> dict | None:
        if condition is None: return None
        df = self._db_.select(schema=self.Schema, table=self.Table, condition=condition, limit=1, legacy=False)
        if df.is_empty(): return None
        row = df.row(0, named=True)
        self._pull_audit_(row)
        return row