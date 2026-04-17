from __future__ import annotations

from dataclasses import dataclass, field

from Library.Database.Dataclass import DataclassAPI
from Library.Database.Enumeration import Enumeration

class AccountType(Enumeration):
    Hedged = 0
    Netted = 1

class MarginMode(Enumeration):
    Sum = 0
    Max = 1
    Net = 2

@dataclass(slots=True, kw_only=True)
class AccountAPI(DataclassAPI):
    AccountType: AccountType | str = field(init=True, repr=True)
    Asset: str = field(init=True, repr=True)
    Balance: float = field(init=True, repr=True)
    Equity: float = field(init=True, repr=True)
    Credit: float = field(init=True, repr=True)
    Leverage: float = field(init=True, repr=True)
    MarginUsed: float = field(init=True, repr=True)
    MarginFree: float = field(init=True, repr=True)
    MarginLevel: float | None = field(init=True, repr=True)
    MarginStopLevel: float = field(init=True, repr=True)
    MarginMode: MarginMode | str = field(init=True, repr=True)

    @staticmethod
    def _as_enum_(cls_: type, value):
        if value is None: return None
        if isinstance(value, cls_): return value
        try: return cls_[value] if isinstance(value, str) else cls_(value)
        except (KeyError, ValueError): return None

    def __post_init__(self):
        self.AccountType = self._as_enum_(AccountType, self.AccountType)
        self.MarginMode = self._as_enum_(MarginMode, self.MarginMode)