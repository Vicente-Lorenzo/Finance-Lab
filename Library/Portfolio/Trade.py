from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from Library.Database.Dataframe import pl
from Library.Database.Database import PrimaryKey
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Dataclass import overridefield
from Library.Portfolio.Portfolio import PortfolioAPI
from Library.Portfolio.Position import PositionAPI
from Library.Market.Timestamp import TimestampAPI
if TYPE_CHECKING: 
    from Library.Database import DatabaseAPI
    from Library.Universe.Contract import ContractAPI

@dataclass(kw_only=True)
class TradeAPI(PositionAPI):

    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = PortfolioAPI.Schema
    Table: ClassVar[str] = "Trade"

    TradeID: int | None = None
    ExitTimestamp: datetime | None = None
    ExitBalance: float | None = None

    _exit_timestamp_: TimestampAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        base = PositionAPI.Structure()
        if cls.ID.PositionID in base:
            base[cls.ID.PositionID] = pl.Int64()
        return {
            cls.ID.TradeID: PrimaryKey(pl.Int64),
            cls.ID.ExitTimestamp: pl.Datetime(),
            cls.ID.ExitBalance: pl.Float64(),
            **base
        }

    def __post_init__(self, db: DatabaseAPI | None, contract: ContractAPI | None) -> None:
        super().__post_init__(db, contract)
        if self.ExitTimestamp:
            self._exit_timestamp_ = TimestampAPI(DateTime=self.ExitTimestamp)

    def _apply_(self, row: dict) -> None:
        super()._apply_(row)
        if self.ExitTimestamp:
            self._exit_timestamp_ = TimestampAPI(DateTime=self.ExitTimestamp)

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = DatapointAPI.pull(self, condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.TradeID: return
        row = DatapointAPI.pull(self,
            condition='"TradeID" = :trade:',
            parameters={"trade": self.TradeID}
        )
        if not row: return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        DatapointAPI.push(self, by=by, key=key or self.ID.TradeID)

    @property
    @overridefield
    def ExitTime(self) -> TimestampAPI | None:
        return self._exit_timestamp_
    @ExitTime.setter
    def ExitTime(self, exit_timestamp: datetime) -> None:
        self.ExitTimestamp = exit_timestamp
        if self._exit_timestamp_: self._exit_timestamp_.DateTime = exit_timestamp
        else: self._exit_timestamp_ = TimestampAPI(DateTime=exit_timestamp)
