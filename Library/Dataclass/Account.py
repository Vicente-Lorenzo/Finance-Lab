from enum import Enum
from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

class AccountType(Enum):
    Hedged = 0
    Netted = 1

class AssetType(Enum):
    USD = 0
    EUR = 1
    GBP = 2
    CAD = 3
    JPY = 4
    AUD = 5
    NZD = 6
    CHF = 7
    Other = 8

class MarginMode(Enum):
    Sum = 0
    Max = 1
    Net = 2

@dataclass(slots=True, kw_only=True)
class AccountAPI(DataclassAPI):
    AccountType: AccountType = field(init=True, repr=True)
    AssetType: AssetType = field(init=True, repr=True)
    Balance: float = field(init=True, repr=True)
    Equity: float = field(init=True, repr=True)
    Credit: float = field(init=True, repr=True)
    Leverage: float = field(init=True, repr=True)
    MarginUsed: float = field(init=True, repr=True)
    MarginFree: float = field(init=True, repr=True)
    MarginLevel: float | None = field(init=True, repr=True)
    MarginStopLevel: float = field(init=True, repr=True)
    MarginMode: MarginMode = field(init=True, repr=True)

    def __post_init__(self):
        self.AccountType = AccountType(self.AccountType)
        self.AssetType = AssetType(self.AssetType)
        self.MarginMode = MarginMode(self.MarginMode)
