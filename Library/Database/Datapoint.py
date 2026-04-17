from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field, InitVar
from datetime import datetime

from Library.Database.Dataframe import pl
from Library.Database.Dataclass import DataclassAPI
if TYPE_CHECKING: from Library.Database.Database import DatabaseAPI

@dataclass(slots=True, kw_only=True)
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
        
    def _audit_(self, actor: str | None = None) -> None:
        now = datetime.now()
        if self.CreatedBy is None:
            self.CreatedBy = actor or "SystemUser"
            self.CreatedAt = now
        self.UpdatedBy = actor or "SystemUser"
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