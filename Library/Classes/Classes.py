import math
from enum import Enum
from datetime import datetime
from typing import Callable, Union
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
        f = getattr(self, name)
        if isinstance(f, Enum): return f.name
        if isinstance(f, Timestamp): return f.Timestamp
        if isinstance(f, Price): return f.Price
        return f
    def data(self, include_fields, include_hidden_fields, include_properties):
        if include_fields:
            for f in fields(self):
                if include_hidden_fields or f.repr:
                    yield f.name, self.parse(f.name)
        if include_properties:
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
    def tuple(self, include_fields=True, include_hidden_fields=True, include_properties=False):
        return tuple([v for _, v in self.data(include_fields=include_fields, include_hidden_fields=include_hidden_fields, include_properties=include_properties)])
    def list(self, include_fields=True, include_hidden_fields=True, include_properties=False):
        return list([v for _, v in self.data(include_fields=include_fields, include_hidden_fields=include_hidden_fields, include_properties=include_properties)])
    def dict(self, include_fields=True, include_hidden_fields=True, include_properties=False):
        return dict({k: v for k, v in self.data(include_fields=include_fields, include_hidden_fields=include_hidden_fields, include_properties=include_properties)})

@dataclass(slots=True, kw_only=True)
class Cycle(Class):
    Value: float = field(init=True, repr=True)
    Period: int = field(default=None, init=True, repr=True)

    @property
    def Radian(self) -> float:
        return 2 * math.pi * self.Value / self.Period
    @property
    def Sin(self):
        return math.sin(self.Radian)
    @property
    def Cos(self):
        return math.cos(self.Radian)

@dataclass(slots=True, kw_only=True)
class Timestamp(Class):
    Timestamp: datetime = field(init=True, repr=True)

    @property
    def Year(self) -> Cycle:
        return Cycle(Value=self.Timestamp.year)
    @property
    def Month(self) -> Cycle:
        return Cycle(Value=self.Timestamp.month, Period=12)
    @property
    def Day(self) -> Cycle:
        return Cycle(Value=self.Timestamp.day, Period=31)
    @property
    def Hour(self) -> Cycle:
        return Cycle(Value=self.Timestamp.hour, Period=24)
    @property
    def Minute(self) -> Cycle:
        return Cycle(Value=self.Timestamp.minute, Period=60)
    @property
    def Second(self) -> Cycle:
        return Cycle(Value=self.Timestamp.second, Period=60)
    @property
    def Millisecond(self) -> Cycle:
        return Cycle(Value=self.Timestamp.microsecond, Period=1000)

@dataclass(slots=True, kw_only=True)
class Price(Class):
    Price: float = field(init=True, repr=True)
    Reference: Union[Price, float] = field(default=None, init=True, repr=True)

    @property
    def Percentage(self):
        return (self.Price / self.Reference) - 1.0
    @property
    def LogPercentage(self) -> float:
        return math.log1p(self.Percentage)

    def __post_init__(self):
        self.Reference = self.Reference.Price if isinstance(self.Reference, Price) else self.Reference

@dataclass(slots=True, kw_only=True)
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

@dataclass(slots=True, kw_only=True)
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
    SwapSummerTime: int = field(default=22, init=True, repr=True)
    SwapWinterTime: int = field(default=21, init=True, repr=True)
    SwapPeriod: int = field(default=24, init=True, repr=True)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

@dataclass(slots=True, kw_only=True)
class Position(Class):
    PositionID: int = field(init=True, repr=True)
    PositionType: PositionType = field(init=True, repr=True)
    TradeType: TradeType = field(init=True, repr=True)
    EntryTimestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    EntryPrice: Union[Price, float] = field(init=True, repr=True)
    Volume: float = field(init=True, repr=True)
    Quantity: float = field(init=True, repr=True)
    Points: float = field(init=True, repr=True)
    Pips: float = field(init=True, repr=True)
    GrossPnL: float = field(init=True, repr=True)
    CommissionPnL: float = field(init=True, repr=True)
    SwapPnL: float = field(init=True, repr=True)
    NetPnL: float = field(init=True, repr=True)

    UsedMargin: float = field(default=None, init=True, repr=True)
    StopLoss: Union[Price, float] = field(default=None, init=True, repr=True)
    TakeProfit: Union[Price, float] = field(default=None, init=True, repr=True)

    DrawdownPoints: float = field(default=0.0, init=False, repr=True)
    DrawdownPips: float = field(default=0.0, init=False, repr=True)
    DrawdownPnL: float = field(default=None, init=False, repr=True)
    DrawdownReturn: float = field(default=None, init=False, repr=True)
    NetReturn: float = field(default=None, init=False, repr=True)
    NetLogReturn: float = field(default=None, init=False, repr=True)
    NetReturnDrawdown: float = field(default=None, init=False, repr=True)
    BaseBalance: float = field(default=None, init=False, repr=True)
    EntryBalance: float = field(default=None, init=False, repr=True)

    def __post_init__(self):
        self.PositionType = PositionType(self.PositionType)
        self.TradeType = TradeType(self.TradeType)
        self.EntryTimestamp = Timestamp(Timestamp=self.EntryTimestamp)
        self.EntryPrice = Price(Price=self.EntryPrice)
        self.StopLoss = None if self.StopLoss is None else float(self.StopLoss)
        self.StopLoss = Price(Price=self.StopLoss, Reference=self.EntryPrice)
        self.TakeProfit = None if self.TakeProfit is None else float(self.TakeProfit)
        self.TakeProfit = Price(Price=self.TakeProfit, Reference=self.EntryPrice)

@dataclass(slots=True, kw_only=True)
class Trade(Position):
    TradeID: int = field(init=True, repr=True)
    ExitTimestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    ExitPrice: Union[Price, float] = field(init=True, repr=True)

    ExitBalance: float = field(default=None, init=False, repr=True)

    def __post_init__(self):
        super().__post_init__()
        self.ExitTimestamp = Timestamp(Timestamp=self.ExitTimestamp)
        self.ExitPrice = Price(Price=self.ExitPrice, Reference=self.EntryPrice)

@dataclass(slots=True)
class Bar(Class):
    Timestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    OpenPrice: Union[Price, float] = field(default=None, init=True, repr=True)
    HighPrice: Union[Price, float] = field(default=None, init=True, repr=True)
    LowPrice: Union[Price, float] = field(default=None, init=True, repr=True)
    ClosePrice: Union[Price, float] = field(default=None, init=True, repr=True)
    TickVolume: Union[Price, float] = field(default=None, init=True, repr=True)

    def __post_init__(self):
        self.Timestamp = Timestamp(Timestamp=self.Timestamp)
        self.OpenPrice = Price(Price=self.OpenPrice)
        self.HighPrice = Price(Price=self.HighPrice, Reference=self.OpenPrice)
        self.LowPrice = Price(Price=self.LowPrice, Reference=self.OpenPrice)
        self.ClosePrice = Price(Price=self.ClosePrice, Reference=self.OpenPrice)

@dataclass(slots=True)
class Tick(Class):
    Timestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    Ask: Union[Price, float] = field(default=None, init=True, repr=True)
    Bid: Union[Price, float] = field(default=None, init=True, repr=True)

    @property
    def Spread(self) -> float:
        return self.Ask - self.Bid

    def __post_init__(self):
        self.Timestamp = Timestamp(Timestamp=self.Timestamp)
        self.Ask = Price(Price=self.Ask, Reference=self.Bid)
        self.Bid = Price(Price=self.Bid, Reference=self.Ask)

@dataclass(slots=True, kw_only=True)
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

@dataclass(slots=True, kw_only=True)
class Telegram(Class):
    Token: str = field(init=True, repr=True)
    ChatID: str = field(init=True, repr=True)
