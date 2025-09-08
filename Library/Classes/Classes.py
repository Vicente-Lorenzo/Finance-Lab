import math
from enum import Enum
from datetime import datetime
from typing import Callable
from dataclasses import dataclass, field, fields

from Library.Classes import *

class Meta(type):
    __slots__ = ()
    def __getattribute__(cls, name):
        if name.startswith("__") and name.endswith("__"):
            return type.__getattribute__(cls, name)
        d = type.__getattribute__(cls, "__dict__")
        v = d.get(name, None)
        if isinstance(v, property):
            return name
        f = d.get("__dataclass_fields__")
        if f is not None and name in f:
            return name
        return type.__getattribute__(cls, name)

@dataclass(slots=True)
class Class(metaclass=Meta):
    def parse(self, name):
        return f.name if isinstance(f := getattr(self, name), Enum) else f
    def data(self):
        for f in fields(self):
            yield f.name, self.parse(f.name)
        p_seen = set()
        for cls in reversed(type(self).mro()):
            if cls is object:
                continue
            for p_name, p in cls.__dict__.items():
                if p_name in p_seen:
                    continue
                if isinstance(p, property):
                    p_seen.add(p_name)
                    yield p_name, self.parse(p_name)
    def tuple(self):
        return tuple([v for _, v in self.data()])
    def list(self):
        return list([v for _, v in self.data()])
    def dict(self):
        return dict({k: v for k, v in self.data()})

@dataclass(slots=True)
class Account(Class):
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

@dataclass(slots=True)
class Symbol(Class):
    BaseAssetType: AssetType = field(init=True, repr=True)
    QuoteAssetType: AssetType = field(init=True, repr=True)
    Digits: int = field(init=True, repr=True)
    PointSize: float = field(init=True, repr=True)
    PipSize: float = field(init=True, repr=True)
    LotSize: int = field(init=True, repr=True)
    VolumeInUnitsMin: float = field(init=True, repr=True)
    VolumeInUnitsMax: float = field(init=True, repr=True)
    VolumeInUnitsStep: float = field(init=True, repr=True)
    Commission: float = field(init=True, repr=True)
    CommissionMode: CommissionMode = field(init=True, repr=True)
    SwapLong: float = field(init=True, repr=True)
    SwapShort: float = field(init=True, repr=True)
    SwapMode: SwapMode = field(init=True, repr=True)
    SwapExtraDay: DayOfWeek = field(init=True, repr=True)
    SwapSummerTime: int = field(init=True, default=22, repr=True)
    SwapWinterTime: int = field(init=True, default=21, repr=True)
    SwapPeriod: int = field(init=True, default=24, repr=True)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

@dataclass(slots=True)
class Position(Class):
    PositionID: int = field(init=True, repr=True)
    PositionType: PositionType = field(init=True, repr=True)
    TradeType: TradeType = field(init=True, repr=True)
    EntryTimestamp: datetime = field(init=True, repr=True)
    EntryPrice: float = field(init=True, repr=True)
    Volume: float = field(init=True, repr=True)
    Quantity: float = field(init=True, repr=True)
    Points: float = field(init=True, repr=True)
    Pips: float = field(init=True, repr=True)
    GrossPnL: float = field(init=True, repr=True)
    CommissionPnL: float = field(init=True, repr=True)
    SwapPnL: float = field(init=True, repr=True)
    NetPnL: float = field(init=True, repr=True)
    StopLoss: float | None = field(init=True, repr=True)
    TakeProfit: float | None = field(init=True, repr=True)
    UsedMargin: float = field(init=True, repr=True)

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
    PositionID: int = field(init=True, repr=True)
    TradeID: int = field(init=True, repr=True)
    PositionType: PositionType = field(init=True, repr=True)
    TradeType: TradeType = field(init=True, repr=True)
    EntryTimestamp: datetime = field(init=True, repr=True)
    ExitTimestamp: datetime = field(init=True, repr=True)
    EntryPrice: float = field(init=True, repr=True)
    ExitPrice: float = field(init=True, repr=True)
    Volume: float = field(init=True, repr=True)
    Quantity: float = field(init=True, repr=True)
    Points: float = field(init=True, repr=True)
    Pips: float = field(init=True, repr=True)
    GrossPnL: float = field(init=True, repr=True)
    CommissionPnL: float = field(init=True, repr=True)
    SwapPnL: float = field(init=True, repr=True)
    NetPnL: float = field(init=True, repr=True)

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
    Timestamp: datetime = field(init=True, repr=True)
    Ask: float = field(init=True, repr=True)
    Bid: float = field(init=True, repr=True)

    @property
    def Spread(self) -> float:
        return self.Ask - self.Bid

@dataclass(slots=True)
class Technical(Class):
    Name: str = field(init=True, repr=True)
    TechnicalType: TechnicalType = field(init=True, repr=True)
    Input: Callable = field(init=True, repr=True)
    Parameters: dict[str, list[list[int | float]]] = field(init=True, repr=True)
    Constraints: Callable = field(init=True, repr=True)
    Function: Callable = field(init=True, repr=True)
    Output: list[str] = field(init=True, repr=True)
    FilterBuy: Callable = field(init=True, repr=True)
    FilterSell: Callable = field(init=True, repr=True)
    SignalBuy: Callable = field(init=True, repr=True)
    SignalSell: Callable = field(init=True, repr=True)

    def __post_init__(self):
        self.TechnicalType = TechnicalType(self.TechnicalType)

@dataclass(slots=True)
class Telegram(Class):
    Token: str = field(init=True, repr=True)
    ChatID: str = field(init=True, repr=True)
