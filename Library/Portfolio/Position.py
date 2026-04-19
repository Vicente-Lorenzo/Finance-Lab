from __future__ import annotations

from typing import ClassVar, Sequence, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, InitVar

from Library.Database.Dataframe import pl
from Library.Database.Database import PrimaryKey, ForeignKey
from Library.Database.Datapoint import DatapointAPI
from Library.Database.Dataclass import overridefield
from Library.Database.Enumeration import as_enum
from Library.Portfolio.Portfolio import PortfolioAPI
from Library.Universe.Universe import UniverseAPI
from Library.Market.Timestamp import TimestampAPI
from Library.Market.Price import PriceAPI
from Library.Portfolio.PnL import PnLAPI
if TYPE_CHECKING: 
    from Library.Database import DatabaseAPI
    from Library.Universe.Contract import ContractAPI

class PositionType(Enum):
    Normal = 0
    Continuation = 1

class TradeType(Enum):
    Buy = 1
    Neutral = 0
    Sell = -1

@dataclass(kw_only=True)
class PositionAPI(DatapointAPI):

    Database: ClassVar[str] = DatapointAPI.Database
    Schema: ClassVar[str] = PortfolioAPI.Schema
    Table: ClassVar[str] = "Position"

    PositionID: int | None = None
    SecurityUID: int | None = None
    
    PositionType: PositionType | str | None = None
    TradeType: TradeType | str | None = None
    
    Volume: float | None = None
    Quantity: float | None = None
    EntryTimestamp: datetime | None = None

    EntryPrice: float | None = None
    StopLossPrice: float | None = None
    TakeProfitPrice: float | None = None
    MaxRunUpPrice: float | None = None
    MaxDrawDownPrice: float | None = None
    ExitPrice: float | None = None

    StopLossPnL: float | None = None
    TakeProfitPnL: float | None = None
    MaxRunUpPnL: float | None = None
    MaxDrawDownPnL: float | None = None
    GrossPnL: float | None = None
    CommissionPnL: float | None = None
    SwapPnL: float | None = None
    NetPnL: float | None = None

    UsedMargin: float | None = None
    EntryBalance: float | None = None
    MidBalance: float | None = None

    contract: InitVar[ContractAPI | None] = field(default=None, init=True, repr=False)

    _entry_timestamp_: TimestampAPI | None = field(default=None, init=False, repr=False)

    _entry_price_: PriceAPI | None = field(default=None, init=False, repr=False)
    _stop_loss_price_: PriceAPI | None = field(default=None, init=False, repr=False)
    _take_profit_price_: PriceAPI | None = field(default=None, init=False, repr=False)
    _max_run_up_price_: PriceAPI | None = field(default=None, init=False, repr=False)
    _max_draw_down_price_: PriceAPI | None = field(default=None, init=False, repr=False)
    _exit_price_: PriceAPI | None = field(default=None, init=False, repr=False)

    _stop_loss_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _take_profit_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _max_draw_down_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _max_run_up_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _gross_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _commission_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _swap_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)
    _net_pn_l_: PnLAPI | None = field(default=None, init=False, repr=False)

    _contract_: ContractAPI | None = field(default=None, init=False, repr=False)

    @classmethod
    def Structure(cls) -> dict:
        from Library.Universe.Security import SecurityAPI
        return {
            cls.ID.PositionID: PrimaryKey(pl.Int64),
            cls.ID.SecurityUID: ForeignKey(pl.Int64, reference=f'"{UniverseAPI.Schema}"."{SecurityAPI.Table}"("{SecurityAPI.ID.UID}")'),
            cls.ID.PositionType: pl.Enum([e.name for e in PositionType]),
            cls.ID.TradeType: pl.Enum([e.name for e in TradeType]),
            cls.ID.Volume: pl.Float64(),
            cls.ID.Quantity: pl.Float64(),
            cls.ID.EntryTimestamp: pl.Datetime(),
            cls.ID.EntryPrice: pl.Float64(),
            cls.ID.StopLossPrice: pl.Float64(),
            cls.ID.TakeProfitPrice: pl.Float64(),
            cls.ID.MaxRunUpPrice: pl.Float64(),
            cls.ID.MaxDrawDownPrice: pl.Float64(),
            cls.ID.ExitPrice: pl.Float64(),
            cls.ID.StopLossPnL: pl.Float64(),
            cls.ID.TakeProfitPnL: pl.Float64(),
            cls.ID.MaxRunUpPnL: pl.Float64(),
            cls.ID.MaxDrawDownPnL: pl.Float64(),
            cls.ID.GrossPnL: pl.Float64(),
            cls.ID.CommissionPnL: pl.Float64(),
            cls.ID.SwapPnL: pl.Float64(),
            cls.ID.NetPnL: pl.Float64(),
            cls.ID.UsedMargin: pl.Float64(),
            cls.ID.EntryBalance: pl.Float64(),
            cls.ID.MidBalance: pl.Float64(),
            **DatapointAPI.Structure()
        }

    def __post_init__(self, db: DatabaseAPI | None, contract: ContractAPI | None) -> None:
        self.PositionType = as_enum(PositionType, self.PositionType)
        self.TradeType = as_enum(TradeType, self.TradeType)
        if not isinstance(contract, property):
            self._contract_ = contract
        self._build_properties_()
        self._db_ = self._connect_(db)
        self._db_.migrate(schema=self.Schema, table=self.Table, structure=self.Structure())
        self.pull()

    def _build_properties_(self):
        if self.EntryTimestamp:
            self._entry_timestamp_ = TimestampAPI(DateTime=self.EntryTimestamp)
        ep = self.EntryPrice
        if ep is not None:
            self._entry_price_ = PriceAPI(Price=ep, Reference=ep, Contract=self._contract_)
            self._stop_loss_price_ = PriceAPI(Price=self.StopLossPrice if self.StopLossPrice is not None else ep, Reference=ep, Contract=self._contract_)
            self._take_profit_price_ = PriceAPI(Price=self.TakeProfitPrice if self.TakeProfitPrice is not None else ep, Reference=ep, Contract=self._contract_)
            self._max_run_up_price_ = PriceAPI(Price=self.MaxRunUpPrice if self.MaxRunUpPrice is not None else ep, Reference=ep, Contract=self._contract_)
            self._max_draw_down_price_ = PriceAPI(Price=self.MaxDrawDownPrice if self.MaxDrawDownPrice is not None else ep, Reference=ep, Contract=self._contract_)
            self._exit_price_ = PriceAPI(Price=self.ExitPrice if self.ExitPrice is not None else ep, Reference=ep, Contract=self._contract_)
        eb = self.EntryBalance
        if eb is not None:
            self._stop_loss_pn_l_ = PnLAPI(PnL=self.StopLossPnL if self.StopLossPnL is not None else 0.0, Reference=eb)
            self._take_profit_pn_l_ = PnLAPI(PnL=self.TakeProfitPnL if self.TakeProfitPnL is not None else 0.0, Reference=eb)
            self._max_run_up_pn_l_ = PnLAPI(PnL=self.MaxRunUpPnL if self.MaxRunUpPnL is not None else 0.0, Reference=eb)
            self._max_draw_down_pn_l_ = PnLAPI(PnL=self.MaxDrawDownPnL if self.MaxDrawDownPnL is not None else 0.0, Reference=eb)
            self._gross_pn_l_ = PnLAPI(PnL=self.GrossPnL if self.GrossPnL is not None else 0.0, Reference=eb)
            self._commission_pn_l_ = PnLAPI(PnL=self.CommissionPnL if self.CommissionPnL is not None else 0.0, Reference=eb)
            self._swap_pn_l_ = PnLAPI(PnL=self.SwapPnL if self.SwapPnL is not None else 0.0, Reference=eb)
            self._net_pn_l_ = PnLAPI(PnL=self.NetPnL if self.NetPnL is not None else 0.0, Reference=eb)

    def _apply_(self, row: dict) -> None:
        for k, v in row.items():
            if hasattr(self, k) and v is not None:
                setattr(self, k, v)
        self.PositionType = as_enum(PositionType, self.PositionType)
        self.TradeType = as_enum(TradeType, self.TradeType)
        self._build_properties_()

    def pull(self, condition: str | None = None, parameters: dict | None = None) -> None:
        if condition:
            row = super().pull(condition=condition, parameters=parameters)
            if row: self._apply_(row)
            return
        if not self.PositionID: return
        row = super().pull(
            condition='"PositionID" = :position:',
            parameters={"position": self.PositionID}
        )
        if not row: return
        self._apply_(row)

    def push(self, by: str, key: str | Sequence[str] | None = None) -> None:
        super().push(by=by, key=key or self.ID.PositionID)

    @property
    @overridefield
    def Contract(self) -> ContractAPI | None:
        return self._contract_
    @Contract.setter
    def Contract(self, contract: ContractAPI | None) -> None:
        self._contract_ = contract
        if self._entry_price_: self._entry_price_.Contract = self._contract_
        if self._stop_loss_price_: self._stop_loss_price_.Contract = self._contract_
        if self._take_profit_price_: self._take_profit_price_.Contract = self._contract_
        if self._max_run_up_price_: self._max_run_up_price_.Contract = self._contract_
        if self._max_draw_down_price_: self._max_draw_down_price_.Contract = self._contract_
        if self._exit_price_: self._exit_price_.Contract = self._contract_