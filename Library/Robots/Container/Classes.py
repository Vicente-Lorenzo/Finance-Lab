from enum import Enum
from datetime import datetime
from typing import Callable
from attrs import define, field, fields

from Agents.Container.Enums import AssetType, PositionType, TradeType, CommissionType, SwapType, DayOfWeek, TechnicalType

@define(slots=True)
class Account:
    Balance: float = field()
    Equity: float = field()

@define(slots=True)
class Symbol:
    BaseAsset: AssetType = field(converter=AssetType)
    QuoteAsset: AssetType = field(converter=AssetType)
    Digits: int = field()
    PipSize: float = field()
    TickSize: float = field()
    LotSize: int = field()
    VolumeInUnitsMin: float = field()
    VolumeInUnitsMax: float = field()
    VolumeInUnitsStep: float = field()
    Commission: float = field()
    CommissionType: CommissionType = field(converter=CommissionType)
    SwapLong: float = field()
    SwapShort: float = field()
    SwapType: SwapType = field(converter=SwapType)
    SwapExtraDay: DayOfWeek = field(converter=DayOfWeek)

@define(slots=True)
class Position:
    PositionID: int = field()
    PositionType: PositionType = field(converter=PositionType)
    TradeType: TradeType = field(converter=TradeType)
    EntryTimestamp: datetime = field()
    EntryPrice: float = field()
    Volume: float = field()
    StopLoss: float | None = field(converter=lambda x: None if x is None else float(x))
    TakeProfit: float | None = field(converter=lambda x: None if x is None else float(x))
    DrawdownPips: float = field(default=0.0)
    DrawdownPnL: float = field(default=None)
    BaseBalance: float = field(default=None)
    EntryBalance: float = field(default=None)

@define(slots=True)
class Trade:
    PositionID: int = field()
    TradeID: int = field()
    PositionType: PositionType = field(converter=PositionType)
    TradeType: TradeType = field(converter=TradeType)
    EntryTimestamp: datetime = field()
    ExitTimestamp: datetime = field()
    EntryPrice: float = field()
    ExitPrice: float = field()
    Volume: float = field()
    GrossPnL: float = field()
    CommissionPnL: float = field()
    SwapPnL: float = field()
    NetPips: float = field()
    NetPnL: float = field()
    DrawdownPips: float = field(default=0.0)
    DrawdownPnL: float = field(default=None)
    DrawdownReturn: float = field(default=None)
    NetReturn: float = field(default=None)
    NetLogReturn: float = field(default=None)
    NetReturnDrawdown: float = field(default=None)
    BaseBalance: float = field(default=None)
    EntryBalance: float = field(default=None)
    ExitBalance: float = field(default=None)

@define(slots=True)
class Bar:
    Timestamp: datetime = field()
    OpenPrice: float = field()
    HighPrice: float = field()
    LowPrice: float = field()
    ClosePrice: float = field()
    TickVolume: float = field()

@define(slots=True)
class Tick:
    Timestamp: datetime = field()
    Ask: float = field()
    Bid: float = field()

@define(slots=True, frozen=True)
class Technical:
    Name: str = field()
    TechnicalType: TechnicalType = field(converter=TechnicalType)
    Input: Callable = field()
    Parameters: dict[str, list[list[int | float]]] = field()
    Constraints: Callable = field()
    Function: Callable = field()
    Output: list[str] = field()
    FilterBuy: Callable = field()
    FilterSell: Callable = field()
    SignalBuy: Callable = field()
    SignalSell: Callable = field()

@define(slots=True, frozen=True)
class TelegramBot:
    Token: str = field()
    ChatID: str = field()

def astuple(instance) -> tuple:
    parse_enum = lambda attribute: attribute.name if isinstance(attribute, Enum) else attribute
    return tuple(parse_enum(getattr(instance, attr.name)) for attr in fields(instance.__class__))
    
