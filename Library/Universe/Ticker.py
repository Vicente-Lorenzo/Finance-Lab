from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import PrimaryKey, ForeignKey
from Library.Universe.Category import CategoryAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(kw_only=True)
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

    def pull(self, condition: str | None = None) -> None:
        if condition:
            row = super().pull(condition=condition)
            if row:
                if not self.UID: self.UID = row.get("UID")
                if self.Category is None: self.Category = row.get("Category")
                if self.BaseAsset is None: self.BaseAsset = row.get("BaseAsset")
                if self.BaseName is None: self.BaseName = row.get("BaseName")
                if self.QuoteAsset is None: self.QuoteAsset = row.get("QuoteAsset")
                if self.QuoteName is None: self.QuoteName = row.get("QuoteName")
                if self.Description is None: self.Description = row.get("Description")
            return
        if not self.UID: return
        escaped = self.UID.replace("'", "''")
        row = super().pull(condition=f"\"UID\" = '{escaped}'")
        if not row: row = super().pull(condition=f"\"Description\" = '{escaped}'")
        if not row:
            if self.BaseAsset is None and self.QuoteAsset is None: raise ValueError(f"Ticker '{self.UID}' not found in database and lacks required fields for creation.")
            return
        if not self.UID: self.UID = row.get("UID")
        if self.Category is None: self.Category = row.get("Category")
        if self.BaseAsset is None: self.BaseAsset = row.get("BaseAsset")
        if self.BaseName is None: self.BaseName = row.get("BaseName")
        if self.QuoteAsset is None: self.QuoteAsset = row.get("QuoteAsset")
        if self.QuoteName is None: self.QuoteName = row.get("QuoteName")
        if self.Description is None: self.Description = row.get("Description")

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.UID)

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