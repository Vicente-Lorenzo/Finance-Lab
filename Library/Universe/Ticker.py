from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import PrimaryKey, ForeignKey
from Library.Universe.Category import CategoryAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(slots=True, kw_only=True)
class TickerAPI(DatapointAPI):

    Table: ClassVar[str] = "Ticker"

    UID: str | None = None
    Category: str | None = None
    BaseAsset: str | None = None
    BaseName: str | None = None
    QuoteAsset: str | None = None
    QuoteName: str | None = None
    Description: str | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.UID: PrimaryKey(pl.String),
            cls.ID.Category: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{CategoryAPI.Table}"("{CategoryAPI.ID.UID}")'),
            cls.ID.BaseAsset: pl.String(),
            cls.ID.BaseName: pl.String(),
            cls.ID.QuoteAsset: pl.String(),
            cls.ID.QuoteName: pl.String(),
            cls.ID.Description: pl.String(),
            **DatapointAPI.Structure()
        }

    @staticmethod
    def normalize(uid: str) -> str:
        import re
        uid = re.sub(r"^[^:]+:", "", uid)
        uid = re.sub(r"[#+\-_]+$", "", uid)
        suffix_list = [
            ".m", ".micro", ".pro", ".p", ".raw", ".ecn", ".s", ".std", ".i", ".ins",
            ".z", ".v", ".x", ".plus", "+", "-", "_sb", ".c", ".cfd"
        ]
        suffix_list.sort(key=len, reverse=True)
        lower_uid = uid.lower()
        for suffix in suffix_list:
            if lower_uid.endswith(suffix):
                uid = uid[:-len(suffix)]
                break
        uid = re.sub(r"[#.+\-_]+$", "", uid)
        return uid.upper()

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if self.UID: self.UID = self.normalize(self.UID)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def pull(self) -> None:
        if not self.UID: return
        escaped = self.UID.replace("'", "''")
        df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"UID\" = '{escaped}'", limit=1, legacy=False)
        if df.is_empty():
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Description\" = '{escaped}'", limit=1, legacy=False)
            
        if df.is_empty():
            if self.BaseAsset is None and self.QuoteAsset is None:
                raise ValueError(f"Ticker '{self.UID}' not found in database and lacks required fields for creation.")
            return
            
        row = df.row(0, named=True)
        if not self.UID: self.UID = row.get("UID")
        if self.Category is None: self.Category = row.get("Category")
        if self.BaseAsset is None: self.BaseAsset = row.get("BaseAsset")
        if self.BaseName is None: self.BaseName = row.get("BaseName")
        if self.QuoteAsset is None: self.QuoteAsset = row.get("QuoteAsset")
        if self.QuoteName is None: self.QuoteName = row.get("QuoteName")
        if self.Description is None: self.Description = row.get("Description")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=self.ID.UID)

    @property
    def Upper(self) -> str:
        return self.UID.upper() if self.UID else ""

    @property
    def Lower(self) -> str:
        return self.UID.lower() if self.UID else ""

    @property
    def Dashed(self) -> str | None:
        if self.BaseAsset and self.QuoteAsset:
            return f"{self.BaseAsset}-{self.QuoteAsset}"
        return None

    @property
    def Slashed(self) -> str | None:
        if self.BaseAsset and self.QuoteAsset:
            return f"{self.BaseAsset}/{self.QuoteAsset}"
        return None

    @property
    def Underscored(self) -> str | None:
        if self.BaseAsset and self.QuoteAsset:
            return f"{self.BaseAsset}_{self.QuoteAsset}"
        return None

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"TickerAPI(UID={self.UID!r}, BaseAsset={self.BaseAsset!r}, QuoteAsset={self.QuoteAsset!r})"