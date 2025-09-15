import math
from enum import Enum
from datetime import datetime
from typing import Callable, Union
from dataclasses import dataclass, field, fields, InitVar

from Library.Classes import *
from Library.Utils import cast

def dynamic(func):
    func._dynamic = True
    return func

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
    def data(self, include_fields, include_hiddens, include_dynamics, include_properties):
        if include_fields:
            for x in fields(self):
                if include_hiddens or x.repr:
                    yield x.name, self.parse(x.name)
        if include_dynamics or include_properties:
            for cls in reversed(type(self).mro()):
                if cls is object:
                    continue
                for x_name, x in cls.__dict__.items():
                    if isinstance(x, property):
                        is_field = getattr(x.fget, "_dynamic", False)
                        if include_dynamics and is_field:
                            yield x_name, self.parse(x_name)
                        if include_properties and not is_field:
                            yield x_name, self.parse(x_name)
    def tuple(self, include_fields=True, include_hiddens=False, include_dynamics=True, include_properties=False):
        return tuple([v for _, v in self.data(include_fields=include_fields, include_hiddens=include_hiddens, include_dynamics=include_dynamics, include_properties=include_properties)])
    def list(self, include_fields=True, include_hiddens=False, include_dynamics=True, include_properties=False):
        return list([v for _, v in self.data(include_fields=include_fields, include_hiddens=include_hiddens, include_dynamics=include_dynamics, include_properties=include_properties)])
    def dict(self, include_fields=True, include_hiddens=False, include_dynamics=True, include_properties=False):
        return dict({k: v for k, v in self.data(include_fields=include_fields, include_hiddens=include_hiddens, include_dynamics=include_dynamics, include_properties=include_properties)})

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
    Timestamp: Union[Timestamp, datetime] = field(init=True, repr=True)

    @property
    def Year(self) -> Cycle:
        return Cycle(Value=self.Timestamp.year)
    @property
    def Month(self) -> Cycle:
        return Cycle(Value=self.Timestamp.month, Period=12)
    @property
    def Weekday(self) -> Cycle:
        return Cycle(Value=self.Timestamp.weekday(), Period=7)
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

    def __post_init__(self):
        self.Timestamp = self.Timestamp.Timestamp if isinstance(self.Timestamp, Timestamp) else self.Timestamp

@dataclass(slots=True, kw_only=True)
class Price(Class):
    Price: Union[Price, float] = field(init=True, repr=True)
    Reference: Union[Price, float] = field(default=None, init=True, repr=True)

    @property
    def Percentage(self):
        return (self.Price / self.Reference) - 1.0
    @property
    def LogPercentage(self) -> float:
        return math.log1p(self.Percentage)

    def __post_init__(self):
        self.Price = self.Price.Price if isinstance(self.Price, Price) else self.Price
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

    _SpotPrice: Union[Price, float] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.BaseAssetType = AssetType(self.BaseAssetType)
        self.QuoteAssetType = AssetType(self.QuoteAssetType)
        self.CommissionMode = CommissionMode(self.CommissionMode)
        self.SwapMode = SwapMode(self.SwapMode)
        self.SwapExtraDay = DayOfWeek(self.SwapExtraDay)

    @property
    def SpotPrice(self) -> Price:
        return self._SpotPrice
    @SpotPrice.setter
    def SpotPrice(self, spot_price: Price):
        self._SpotPrice = Price(Price=spot_price)
    @property
    def PointValue(self) -> float:
        return self.PointSize * self.LotSize / self.SpotPrice.Price
    @property
    def PipValue(self) -> float:
        return self.PipSize * self.LotSize / self.SpotPrice.Price

@dataclass(slots=True, kw_only=True)
class Position(Class):
    PositionID: int = field(init=True, repr=True)
    PositionType: PositionType = field(init=True, repr=True)
    TradeType: TradeType = field(init=True, repr=True)
    EntryTimestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    EntryPrice: InitVar[Union[Price, float]] = field(init=True, repr=True)
    Volume: float = field(init=True, repr=True)
    Quantity: float = field(init=True, repr=True)
    Points: float = field(init=True, repr=True)
    Pips: float = field(init=True, repr=True)
    GrossPnL: float = field(init=True, repr=True)
    CommissionPnL: float = field(init=True, repr=True)
    SwapPnL: float = field(init=True, repr=True)
    NetPnL: float = field(init=True, repr=True)

    UsedMargin: float = field(default=None, init=True, repr=True)
    StopLoss: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    TakeProfit: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)

    DrawdownPoints: float = field(default=0.0, init=False, repr=True)
    DrawdownPips: float = field(default=0.0, init=False, repr=True)
    DrawdownPnL: float = field(default=None, init=False, repr=True)
    DrawdownReturn: float = field(default=None, init=False, repr=True)
    NetReturn: float = field(default=None, init=False, repr=True)
    NetLogReturn: float = field(default=None, init=False, repr=True)
    NetReturnDrawdown: float = field(default=None, init=False, repr=True)
    BaseBalance: float = field(default=None, init=False, repr=True)
    EntryBalance: float = field(default=None, init=False, repr=True)

    _EntryPrice: Union[Price, float] = field(default=None, init=False, repr=False)
    _StopLoss: Union[Price, float] = field(default=None, init=False, repr=False)
    _TakeProfit: Union[Price, float] = field(default=None, init=False, repr=False)

    def __post_init__(self, entry_price: Union[Price, float], stop_loss: Union[Price, float], take_profit: Union[Price, float]):
        self.PositionType = PositionType(self.PositionType)
        self.TradeType = TradeType(self.TradeType)
        self.EntryTimestamp = Timestamp(Timestamp=self.EntryTimestamp)
        self._EntryPrice = Price(Price=entry_price)
        self._StopLoss = Price(Price=cast(stop_loss, float, None), Reference=entry_price)
        self._TakeProfit = Price(Price=cast(take_profit, float, None), Reference=entry_price)

    @property
    @dynamic
    def EntryPrice(self) -> Price:
        return self._EntryPrice
    @EntryPrice.setter
    def EntryPrice(self, entry_price: Union[Price, float]) -> None:
        self._EntryPrice = Price(Price=entry_price)
        self.StopLoss = self._StopLoss
        self.TakeProfit = self._TakeProfit
    @property
    @dynamic
    def StopLoss(self) -> Price:
        return self._StopLoss
    @StopLoss.setter
    def StopLoss(self, stop_loss: Union[Price, float]) -> None:
        self._StopLoss = Price(Price=cast(stop_loss, float, None), Reference=self._EntryPrice)
    @property
    @dynamic
    def TakeProfit(self) -> Price:
        return self._TakeProfit
    @TakeProfit.setter
    def TakeProfit(self, take_profit: Union[Price, float]) -> None:
        self._TakeProfit = Price(Price=cast(take_profit, float, None), Reference=self._EntryPrice)

@dataclass(slots=True, kw_only=True)
class Trade(Position):
    TradeID: int = field(init=True, repr=True)
    ExitTimestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    ExitPrice: InitVar[Union[Price, float]] = field(init=True, repr=True)

    ExitBalance: float = field(default=None, init=False, repr=True)

    _ExitPrice: Union[Price, float] = field(default=None, init=False, repr=False)

    def __post_init__(self, entry_price: Union[Price, float], stop_loss: Union[Price, float], take_profit: Union[Price, float], exit_price: Union[Price, float]):
        super(Trade, self).__post_init__(entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit)
        self.ExitTimestamp = Timestamp(Timestamp=self.ExitTimestamp)
        self._ExitPrice = Price(Price=exit_price, Reference=entry_price)

    @property
    @dynamic
    def EntryPrice(self) -> Price:
        return self._EntryPrice
    @EntryPrice.setter
    def EntryPrice(self, entry_price: Union[Price, float]) -> None:
        self._EntryPrice = Price(Price=entry_price)
        self.StopLoss = self._StopLoss
        self.TakeProfit = self._TakeProfit
        self.ExitPrice = self._ExitPrice
    @property
    @dynamic
    def ExitPrice(self) -> Price:
        return self._ExitPrice
    @ExitPrice.setter
    def ExitPrice(self, exit_price: Union[Price, float]) -> None:
        self._ExitPrice = Price(Price=exit_price, Reference=self._EntryPrice)

@dataclass(slots=True)
class Bar(Class):
    Timestamp: Union[Timestamp, datetime] = field(default=None, init=True, repr=True)
    OpenPrice: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    HighPrice: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    LowPrice: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    ClosePrice: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    TickVolume: float = field(default=None, init=True, repr=True)

    _OpenPrice: Union[Price, float] = field(default=None, init=False, repr=False)
    _HighPrice: Union[Price, float] = field(default=None, init=False, repr=False)
    _LowPrice: Union[Price, float] = field(default=None, init=False, repr=False)
    _ClosePrice: Union[Price, float] = field(default=None, init=False, repr=False)

    def __post_init__(self, open_price: Union[Price, float], high_price: Union[Price, float], low_price: Union[Price, float], close_price: Union[Price, float]):
        self.Timestamp = Timestamp(Timestamp=self.Timestamp)
        self._OpenPrice = Price(Price=open_price)
        self._HighPrice = Price(Price=high_price, Reference=open_price)
        self._LowPrice = Price(Price=low_price, Reference=open_price)
        self._ClosePrice = Price(Price=close_price, Reference=open_price)

    @property
    @dynamic
    def OpenPrice(self) -> Price:
        return self._OpenPrice
    @OpenPrice.setter
    def OpenPrice(self, open_price: Union[Price, float]) -> None:
        self._OpenPrice = Price(Price=open_price)
        self.HighPrice = self._HighPrice
        self.LowPrice = self._LowPrice
        self.ClosePrice = self._ClosePrice
    @property
    @dynamic
    def HighPrice(self) -> Price:
        return self._HighPrice
    @HighPrice.setter
    def HighPrice(self, high_price: Union[Price, float]) -> None:
        self._HighPrice = Price(Price=high_price, Reference=self._OpenPrice)
    @property
    @dynamic
    def LowPrice(self) -> Price:
        return self._LowPrice
    @LowPrice.setter
    def LowPrice(self, low_price: Union[Price, float]) -> None:
        self._LowPrice = Price(Price=low_price, Reference=self._OpenPrice)
    @property
    @dynamic
    def ClosePrice(self) -> Price:
        return self._ClosePrice
    @ClosePrice.setter
    def ClosePrice(self, close_price: Union[Price, float]) -> None:
        self._ClosePrice = Price(Price=close_price, Reference=self._OpenPrice)

@dataclass(slots=True)
class Tick(Class):
    Timestamp: Union[Timestamp, datetime] = field(init=True, repr=True)
    Ask: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)
    Bid: InitVar[Union[Price, float]] = field(default=None, init=True, repr=True)

    _Ask: Union[Price, float] = field(default=None, init=False, repr=False)
    _Bid: Union[Price, float] = field(default=None, init=False, repr=False)

    def __post_init__(self, ask: Union[Price, float], bid: Union[Price, float]):
        self.Timestamp = Timestamp(Timestamp=self.Timestamp)
        self._Ask = Price(Price=ask, Reference=bid)
        self._Bid = Price(Price=bid, Reference=ask)

    @property
    @dynamic
    def Ask(self) -> Price:
        return self._Ask
    @Ask.setter
    def Ask(self, ask: Union[Price, float]) -> None:
        self._Ask = Price(Price=ask, Reference=self._Bid)
    @property
    @dynamic
    def Bid(self) -> Price:
        return self._Bid
    @Bid.setter
    def Bid(self, bid: Union[Price, float]) -> None:
        self._Bid = Price(Price=bid, Reference=self._Ask)

    @property
    def Spread(self) -> Price:
        return Price(Price=self.Ask.Price - self.Bid.Price, Reference=self._Ask)

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
