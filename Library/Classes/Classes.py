import math
from enum import Enum
from abc import ABC
from datetime import datetime
from typing import Callable
from dataclasses import dataclass, field, fields

from Library.Classes import *

@dataclass(slots=True)
class Class(ABC):
    def repr(self, hidden: bool = False):
        for f in fields(self):
            if hidden or f.repr:
                yield f
    def tuple(self, hidden: bool = False) -> tuple:
        return tuple([getattr(self, f.name) for f in self.repr(hidden=hidden)])
    def list(self, hidden: bool = False) -> list:
        return list([getattr(self, f.name) for f in self.repr(hidden=hidden)])
    def dict(self, hidden: bool = False) -> dict:
        return {f.name: getattr(self, f.name) for f in self.repr(hidden=hidden)}

@dataclass(slots=True)
class Account(Class):
    AccountType: AccountType
    AssetType: AssetType
    Balance: float
    Equity: float
    Credit: float
    Leverage: float
    MarginUsed: float
    MarginFree: float
    MarginLevel: float | None
    MarginStopLevel: float
    MarginMode: MarginMode

    def __post_init__(self):
        self.AccountType = AccountType(self.AccountType)
        self.AssetType = AssetType(self.AssetType)
        self.MarginMode = MarginMode(self.MarginMode)

@dataclass(slots=True)
class Symbol(Class):
    BaseAssetType: AssetType
    QuoteAssetType: AssetType
    Digits: int
    PointSize: float
    PipSize: float
    LotSize: int
    VolumeInUnitsMin: float
    VolumeInUnitsMax: float
    VolumeInUnitsStep: float
    Commission: float
    CommissionMode: CommissionMode
    SwapLong: float
    SwapShort: float
    SwapMode: SwapMode
    SwapExtraDay: DayOfWeek
    SwapSummerTime: int = field(default=22)
    SwapWinterTime: int = field(default=21)
    SwapPeriod: int = field(default=24)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

@dataclass(slots=True)
class Position(Class):
    PositionID: int
    PositionType: PositionType
    TradeType: TradeType
    EntryTimestamp: datetime
    EntryPrice: float
    Volume: float
    Quantity: float
    Points: float
    Pips: float
    GrossPnL: float
    CommissionPnL: float
    SwapPnL: float
    NetPnL: float
    StopLoss: float | None
    TakeProfit: float | None
    UsedMargin: float
    DrawdownPoints: float = field(default=0.0, init=False)
    DrawdownPips: float = field(default=0.0, init=False)
    DrawdownPnL: float = field(default=None, init=False)
    DrawdownReturn: float = field(default=None, init=False)
    NetReturn: float = field(default=None, init=False)
    NetLogReturn: float = field(default=None, init=False)
    NetReturnDrawdown: float = field(default=None, init=False)
    BaseBalance: float = field(default=None, init=False)
    EntryBalance: float = field(default=None, init=False)

    def __post_init__(self):
        self.PositionType = PositionType(self.PositionType)
        self.TradeType = TradeType(self.TradeType)
        self.StopLoss = None if self.StopLoss is None else float(self.StopLoss)
        self.TakeProfit = None if self.TakeProfit is None else float(self.TakeProfit)

@dataclass(slots=True)
class Trade(Class):
    PositionID: int
    TradeID: int
    PositionType: PositionType
    TradeType: TradeType
    EntryTimestamp: datetime
    ExitTimestamp: datetime
    EntryPrice: float
    ExitPrice: float
    Volume: float
    Quantity: float
    Points: float
    Pips: float
    GrossPnL: float
    CommissionPnL: float
    SwapPnL: float
    NetPnL: float
    DrawdownPoints: float = field(default=0.0, init=False)
    DrawdownPips: float = field(default=0.0, init=False)
    DrawdownPnL: float = field(default=None, init=False)
    DrawdownReturn: float = field(default=None, init=False)
    NetReturn: float = field(default=None, init=False)
    NetLogReturn: float = field(default=None, init=False)
    NetReturnDrawdown: float = field(default=None, init=False)
    BaseBalance: float = field(default=None, init=False)
    EntryBalance: float = field(default=None, init=False)
    ExitBalance: float = field(default=None, init=False)

    def __post_init__(self):
        self.PositionType = PositionType(self.PositionType)
        self.TradeType = TradeType(self.TradeType)

@dataclass(slots=True)
class Bar(Class):
    Timestamp: datetime = field(init=True, repr=True)
    OpenPrice: float = field(init=True, repr=True)
    HighPrice: float = field(init=True, repr=True)
    LowPrice: float = field(init=True, repr=True)
    ClosePrice: float = field(init=True, repr=True)
    TickVolume: float = field(init=True, repr=True)

    @property
    def HighReturn(self) -> float:
        return (self.HighPrice / self.OpenPrice) - 1.0

    @property
    def HighLogReturn(self) -> float:
        return math.log1p(self.HighReturn)

    @property
    def LowReturn(self) -> float:
        return (self.LowPrice / self.OpenPrice) - 1.0

    @property
    def LowLogReturn(self) -> float:
        return math.log1p(self.LowReturn)

    @property
    def CloseReturn(self) -> float:
        return (self.ClosePrice / self.OpenPrice) - 1.0

    @property
    def CloseLogReturn(self) -> float:
        return math.log1p(self.CloseReturn)

@dataclass(slots=True)
class Tick(Class):
    Timestamp: datetime
    Ask: float
    Bid: float
    Spread: float = field(init=False)

    def __post_init__(self):
        self.Spread = self.Ask - self.Bid

@dataclass(slots=True)
class Technical(Class):
    Name: str
    TechnicalType: TechnicalType
    Input: Callable
    Parameters: dict[str, list[list[int | float]]]
    Constraints: Callable
    Function: Callable
    Output: list[str]
    FilterBuy: Callable
    FilterSell: Callable
    SignalBuy: Callable
    SignalSell: Callable

    def __post_init__(self):
        self.TechnicalType = TechnicalType(self.TechnicalType)

@dataclass(slots=True)
class Telegram(Class):
    Token: str
    ChatID: str
