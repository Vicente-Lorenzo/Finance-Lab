from __future__ import annotations

import re
from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import Enumeration
from Library.Database import PrimaryKey, ForeignKey
from Library.Universe.Category import CategoryAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

_FUTURES_PATTERNS_ = (
    re.compile(r"-F$"),
    re.compile(r"-[A-Z]{3}\d{2}$"),
    re.compile(r"[FGHJKMNQUVXZ]\d{1,2}$"),
    re.compile(r"\d!$"),
)
_PREFIX_PATTERN_ = re.compile(r"^[^:]+:")
_TRIM_PATTERN_ = re.compile(r"[#.+\-_]+$")
_SUFFIX_LIST_ = sorted(
    [".m", ".micro", ".pro", ".p", ".raw", ".ecn", ".s", ".std", ".i", ".ins",
     ".z", ".v", ".x", ".plus", "+", "-", "_sb", ".c", ".cfd"],
    key=len, reverse=True
)

class Instrument(Enumeration):
    Spot = 0
    Future = 1
    Swap = 2
    Option = 3

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
        uid = _PREFIX_PATTERN_.sub("", uid)
        uid = _TRIM_PATTERN_.sub("", uid)
        for pattern in _FUTURES_PATTERNS_: uid = pattern.sub("", uid)
        lower_uid = uid.lower()
        for suffix in _SUFFIX_LIST_:
            if lower_uid.endswith(suffix):
                uid = uid[:-len(suffix)]
                break
        uid = _TRIM_PATTERN_.sub("", uid)
        return uid.upper()

    @staticmethod
    def detect(uid: str) -> Instrument:
        for pattern in _FUTURES_PATTERNS_:
            if pattern.search(uid): return Instrument.Future
        return Instrument.Spot

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if self.UID: self.UID = self.normalize(self.UID)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _apply_(self, row: dict) -> None:
        if not self.UID: self.UID = row.get("UID")
        if self.Category is None: self.Category = row.get("Category")
        if self.BaseAsset is None: self.BaseAsset = row.get("BaseAsset")
        if self.BaseName is None: self.BaseName = row.get("BaseName")
        if self.QuoteAsset is None: self.QuoteAsset = row.get("QuoteAsset")
        if self.QuoteName is None: self.QuoteName = row.get("QuoteName")
        if self.Description is None: self.Description = row.get("Description")

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.UID: return
        row = super().pull(
            condition='"UID" = :value: OR "Description" = :value:',
            parameters={"value": self.UID}
        )
        if not row:
            if self.BaseAsset is None and self.QuoteAsset is None: raise ValueError(f"Ticker '{self.UID}' not found in database and lacks required fields for creation.")
            return
        self._apply_(row)

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