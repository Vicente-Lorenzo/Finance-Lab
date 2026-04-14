import re
from typing_extensions import Self
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import DataclassAPI

def _instances_(cls):
    cls.M1 = cls("M1")
    cls.M5 = cls("M5")
    cls.M15 = cls("M15")
    cls.H1 = cls("H1")
    cls.H4 = cls("H4")
    cls.D1 = cls("D1")
    cls.W1 = cls("W1")
    cls.MN1 = cls("MN1")
    return cls

@_instances_
@dataclass(slots=True)
class TimeframeAPI(DataclassAPI):
    Raw: InitVar[str | Self]
    
    _Unit_: str = field(init=False, repr=False)
    _Value_: int = field(init=False, repr=False)

    def __post_init__(self, raw: str | Self):
        if isinstance(raw, type(self)):
            self._Unit_ = raw._Unit_
            self._Value_ = raw._Value_
        else:
            self._Unit_, self._Value_ = self._decode_(raw)

    @staticmethod
    def _decode_(value: str) -> tuple[str, int]:
        match = re.match(r'^(\d*)([A-Za-z]+)(\d*)$', str(value).strip())
        if not match: return "M", 1
        prefix_digit, unit_str, suffix_digit = match.groups()
        value_int = int(prefix_digit or suffix_digit or 1)
        u = unit_str.upper()
        if u.startswith("MN") or "MONTH" in u: unit = "MN"
        elif u.startswith("M"): unit = "M"
        elif u.startswith("H"): unit = "H"
        elif u.startswith("D"): unit = "D"
        elif u.startswith("W"): unit = "W"
        elif u.startswith("S"): unit = "S"
        elif u.startswith("Y"): unit = "Y"
        else: unit = "M"
        return unit, value_int

    @property
    def Short(self) -> str:
        return f"{self._Unit_}{self._Value_}"

    @property
    def Long(self) -> str:
        mapping = {"S": "Second", "M": "Minute", "H": "Hour", "D": "Day", "W": "Week", "MN": "Month", "Y": "Year"}
        unit = mapping.get(self._Unit_, "Minute")
        if self._Value_ == 1: return unit
        return f"{unit}{self._Value_}"

    @property
    def Frequency(self) -> str:
        mapping = {"D": "DAILY", "W": "WEEKLY", "MN": "MONTHLY", "Y": "YEARLY"}
        if self._Value_ == 1 and self._Unit_ in mapping:
            return mapping[self._Unit_]
        return self.Long.upper()

    @property
    def Minutes(self) -> float:
        mapping = {"S": 1/60, "M": 1, "H": 60, "D": 1440, "W": 10080, "MN": 43200, "Y": 525600}
        return self._Value_ * mapping.get(self._Unit_, 1)

    @property
    def Hours(self) -> float:
        return self.Minutes / 60

    @property
    def Seconds(self) -> float:
        return self.Minutes * 60

    def __str__(self) -> str:
        return self.Short