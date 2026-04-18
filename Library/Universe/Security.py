from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from dataclasses import dataclass
from functools import cached_property

from Library.Database.Dataframe import pl
from Library.Database.Enumeration import as_enum
from Library.Database.Database import IdentityKey, PrimaryKey, ForeignKey
from Library.Universe.Ticker import TickerAPI, Contract
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI
from Library.Universe.Contract import ContractAPI
from Library.Database.Datapoint import DatapointAPI
if TYPE_CHECKING: from Library.Database import DatabaseAPI

@dataclass(kw_only=True)
class SecurityAPI(DatapointAPI):

    Table: ClassVar[str] = "Security"

    UID: int | None = None

    ProviderUID: str
    CategoryUID: str | None = None
    TickerUID: str
    ContractUID: Contract | str | None = None

    @classmethod
    def Structure(cls) -> dict:
        return {
            cls.ID.UID: IdentityKey(pl.Int64),
            cls.ID.ProviderUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{ProviderAPI.Table}"("{ProviderAPI.ID.UID}")', primary=True),
            cls.ID.CategoryUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{CategoryAPI.Table}"("{CategoryAPI.ID.UID}")', primary=True),
            cls.ID.TickerUID: ForeignKey(pl.String, reference=f'"{DatapointAPI.Schema}"."{TickerAPI.Table}"("{TickerAPI.ID.UID}")', primary=True),
            cls.ID.ContractUID: PrimaryKey(pl.Enum([i.name for i in Contract])),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None) -> None:
        if not self.ContractUID: self.ContractUID = TickerAPI.detect(self.TickerUID)
        self.ContractUID = as_enum(Contract, self.ContractUID)
        self.TickerUID = TickerAPI.normalize(self.TickerUID)
        self.ProviderUID = ProviderAPI.normalize(self.ProviderUID)
        self._db_ = self._connect_(db)
        if not self.CategoryUID:
            t = TickerAPI(UID=self.TickerUID, db=self._db_)
            self.CategoryUID = t.Category or ""
        self._db_.migrate(schema=DatapointAPI.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _apply_(self, row: dict) -> None:
        if self.UID is None: self.UID = row.get("UID")
        if not self.CategoryUID: self.CategoryUID = row.get("CategoryUID")
        if not self.ContractUID: self.ContractUID = as_enum(Contract, row.get("ContractUID"))

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        contract = self.ContractUID.name if isinstance(self.ContractUID, Contract) else self.ContractUID
        params = {"provider": self.ProviderUID, "ticker": self.TickerUID, "contract": contract}
        clauses = ['"ProviderUID" = :provider:', '"TickerUID" = :ticker:', '"ContractUID" = :contract:']
        if self.CategoryUID:
            clauses.insert(1, '"CategoryUID" = :category:')
            params["category"] = self.CategoryUID
        row = super().pull(condition=" AND ".join(clauses), parameters=params)
        if not row:
            if not self.CategoryUID: raise ValueError(f"Security '{self.TickerUID}@{self.ProviderUID}' not found in database.")
            return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        self.Ticker.push(by=by)
        self.Provider.push(by=by)
        if self.CategoryUID: self.Category.push(by=by)
        self.Contract.push(by=by)
        super().push(by=by, key=key or [self.ID.ProviderUID, self.ID.CategoryUID, self.ID.TickerUID, self.ID.ContractUID])
        if self.UID is None: self.pull()

    @cached_property
    def Ticker(self) -> TickerAPI:
        return TickerAPI(UID=self.TickerUID, db=self._db_)

    @cached_property
    def Provider(self) -> ProviderAPI:
        return ProviderAPI(UID=self.ProviderUID, db=self._db_)

    @cached_property
    def Contract(self) -> ContractAPI:
        return ContractAPI(TickerUID=self.TickerUID, ProviderUID=self.ProviderUID, UID=self.ContractUID, db=self._db_)

    @cached_property
    def Category(self) -> CategoryAPI:
        return CategoryAPI(UID=self.CategoryUID, db=self._db_)

    def __str__(self) -> str:
        return f"{self.TickerUID}@{self.ProviderUID}"

    def __repr__(self) -> str:
        return f"SecurityAPI(UID={self.UID!r}, ProviderUID={self.ProviderUID!r}, CategoryUID={self.CategoryUID!r}, TickerUID={self.TickerUID!r}, ContractUID={self.ContractUID!r})"