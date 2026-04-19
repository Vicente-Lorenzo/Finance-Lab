from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

from Library.Database.Dataframe import pl
from Library.Database.Database import PrimaryKey, ForeignKey
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Enumeration import as_enum
from Library.Portfolio.Portfolio import PortfolioAPI
from Library.Universe.Universe import UniverseAPI
if TYPE_CHECKING:
    from Library.Database import DatabaseAPI

class AccountType(Enum):
    Hedged = 0
    Netted = 1

class MarginMode(Enum):
    Sum = 0
    Max = 1
    Net = 2

class Environment(Enum):
    Live = 0
    Demo = 1

@dataclass(kw_only=True)
class AccountAPI(DatapointAPI):

    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = PortfolioAPI.Schema
    Table: ClassVar[str] = "Account"

    UID: str | None = None
    ProviderUID: str | None = None
    Environment: Environment | str | None = None
    AccountType: AccountType | str | None = None
    MarginMode: MarginMode | str | None = None
    
    Asset: str | None = None
    Balance: float | None = None
    Equity: float | None = None
    Credit: float | None = None
    Leverage: float | None = None
    MarginUsed: float | None = None
    MarginFree: float | None = None
    MarginLevel: float | None = None
    MarginStopLevel: float | None = None

    @classmethod
    def Structure(cls) -> dict:
        from Library.Universe.Provider import ProviderAPI
        return {
            cls.ID.UID: PrimaryKey(pl.String),
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{UniverseAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")'),
            cls.ID.Environment: pl.Enum([e.name for e in Environment]),
            cls.ID.AccountType: pl.Enum([e.name for e in AccountType]),
            cls.ID.MarginMode: pl.Enum([e.name for e in MarginMode]),
            cls.ID.Asset: pl.String(),
            cls.ID.Balance: pl.Float64(),
            cls.ID.Equity: pl.Float64(),
            cls.ID.Credit: pl.Float64(),
            cls.ID.Leverage: pl.Float64(),
            cls.ID.MarginUsed: pl.Float64(),
            cls.ID.MarginFree: pl.Float64(),
            cls.ID.MarginLevel: pl.Float64(),
            cls.ID.MarginStopLevel: pl.Float64(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        self.Environment = as_enum(Environment, self.Environment)
        self.AccountType = as_enum(AccountType, self.AccountType)
        self.MarginMode = as_enum(MarginMode, self.MarginMode)
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=self.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _apply_(self, row: dict) -> None:
        for k, v in row.items():
            if hasattr(self, k) and v is not None:
                setattr(self, k, v)
        self.Environment = as_enum(Environment, self.Environment)
        self.AccountType = as_enum(AccountType, self.AccountType)
        self.MarginMode = as_enum(MarginMode, self.MarginMode)

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.UID: return
        row = super().pull(
            condition='"UID" = :uid:',
            parameters={"uid": self.UID}
        )
        if not row: return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.UID)