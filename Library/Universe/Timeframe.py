from __future__ import annotations

import re
from typing import ClassVar, TYPE_CHECKING
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database import PrimaryKey
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

_UNIT_MAP_ = {"S": "Second", "M": "Minute", "H": "Hour", "D": "Day", "W": "Week", "MN": "Month", "Y": "Year"}
_MINUTES_MAP_ = {"S": 1 / 60, "M": 1, "H": 60, "D": 1440, "W": 10080, "MN": 43200, "Y": 525600}

@dataclass(slots=True, kw_only=True)
class TimeframeAPI(DatapointAPI):

    Table: ClassVar[str] = "Timeframe"

    UID: str | None = None
    Name: str | None = None
    Unit: str | None = None
    Value: int | None = None

    _db_: DatabaseAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.UID: PrimaryKey(pl.String),
            cls.ID.Name: pl.String(),
            cls.ID.Unit: pl.String(),
            cls.ID.Value: pl.Int32(),
            **DatapointAPI.Structure()
        }

    @staticmethod
    def normalize(uid: str) -> str:
        if not uid: return ""
        uid = str(uid).strip().upper()
        if uid in ["DAILY", "D", "DAY", "1D"]: return "D1"
        if uid in ["WEEKLY", "W", "WEEK", "1W"]: return "W1"
        if uid in ["MONTHLY", "MN", "MONTH", "1MN"]: return "MN1"
        if uid in ["HOURLY", "H", "HOUR", "1H", "60", "60M"]: return "H1"
        if uid in ["MINUTELY", "M", "MINUTE", "1M"]: return "M1"
        if uid in ["SECONDLY", "S", "SECOND", "1S"]: return "S1"
        if uid in ["YEARLY", "Y", "YEAR", "1Y"]: return "Y1"
        
        match = re.match(r"^(\d*)([A-Z]+)(\d*)$", uid)
        if match:
            prefix, unit, suffix = match.groups()
            v = int(prefix or suffix or 1)
            if unit.startswith("MN"): unit = "MN"
            elif unit.startswith("M"): unit = "M"
            elif unit.startswith("H"): unit = "H"
            elif unit.startswith("D"): unit = "D"
            elif unit.startswith("W"): unit = "W"
            elif unit.startswith("S"): unit = "S"
            elif unit.startswith("Y"): unit = "Y"
            return f"{unit}{v}"
        return uid

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if self.UID: self.UID = self.normalize(self.UID)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()
        if not self.Unit: self._infer_()

    def _infer_(self) -> None:
        if not self.UID: return
        match = re.match(r"^([A-Z]+)(\d*)$", self.UID)
        if not match: return
        unit, suffix = match.groups()
        v = int(suffix or 1)
        self.Unit = unit
        self.Value = v
        name = _UNIT_MAP_.get(unit, "Minute")
        self.Name = name if v == 1 else f"{name}{v}"

    def pull(self) -> None:
        if not self.UID: return
        escaped = self.UID.replace("'", "''")
        df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"UID\" = '{escaped}'", limit=1, legacy=False)
        if df.is_empty():
            df = self._db_.select(schema=DatapointAPI.Schema, table=self.Table, condition=f"\"Name\" = '{escaped}'", limit=1, legacy=False)

        if df.is_empty():
            if self.Unit is None and not re.match(r"^([A-Z]+)(\d*)$", self.UID):
                raise ValueError(f"Timeframe '{self.UID}' not found in database and lacks correct format for creation.")
            return
            
        row = df.row(0, named=True)
        if not self.UID: self.UID = row.get("UID")
        if self.Name is None: self.Name = row.get("Name")
        if self.Unit is None: self.Unit = row.get("Unit")
        if self.Value is None: self.Value = row.get("Value")
        self._pull_audit_(row)

    def push(self, by: str = "SystemUser") -> None:
        self._audit_(by)
        data = self.dict(include_fields=True, include_properties=False, include_override_fields=False)
        valid_keys = self.Structure().keys()
        clean_data = {k: v for k, v in data.items() if k in valid_keys}
        self._db_.upsert(schema=DatapointAPI.Schema, table=self.Table, data=clean_data, key=self.ID.UID)

    @property
    def Minutes(self) -> float | None:
        if self.Value is None or self.Unit is None: return None
        return self.Value * _MINUTES_MAP_.get(self.Unit, 1)

    @property
    def Hours(self) -> float | None:
        minutes = self.Minutes
        return minutes / 60 if minutes is not None else None

    @property
    def Seconds(self) -> float | None:
        minutes = self.Minutes
        return minutes * 60 if minutes is not None else None

    def __str__(self) -> str:
        return self.UID or ""

    def __repr__(self) -> str:
        return f"TimeframeAPI(UID={self.UID!r}, Name={self.Name!r}, Unit={self.Unit!r}, Value={self.Value!r})"