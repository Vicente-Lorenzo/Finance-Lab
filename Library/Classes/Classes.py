from enum import Enum
from datetime import datetime
from typing import Callable
from dataclasses import dataclass, field, fields

from Library.Classes import *

@dataclass(slots=True)
class Account:
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
class Symbol:
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
    SwapTime: int = field(default=21)
    SwapPeriod: int = field(default=24)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

@dataclass(slots=True)
class Position:
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
class Trade:
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
class Bar:
    Timestamp: datetime
    OpenPrice: float
    HighPrice: float
    LowPrice: float
    ClosePrice: float
    TickVolume: float

@dataclass(slots=True)
class Tick:
    Timestamp: datetime
    Ask: float
    Bid: float
    Spread: float = field(init=False)

    def __post_init__(self):
        self.Spread = self.Ask - self.Bid

@dataclass(slots=True)
class Technical:
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

@dataclass(slots=True, frozen=True)
class Telegram:
    Token: str
    ChatID: str

def astuple(instance) -> tuple:
    def parse_enum(attr): return attr.name if isinstance(attr, Enum) else attr
    return tuple(parse_enum(getattr(instance, f.name)) for f in fields(instance.__class__))
