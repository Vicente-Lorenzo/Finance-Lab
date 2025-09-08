from enum import Enum
from typing import Union
from dataclasses import dataclass

from Library.Classes import *

class UpdateID(Enum):
    Complete = 0
    Account = 1
    Symbol = 2
    OpenedBuy = 3
    OpenedSell = 4
    ModifiedBuyVolume = 5
    ModifiedBuyStopLoss = 6
    ModifiedBuyTakeProfit = 7
    ModifiedSellVolume = 8
    ModifiedSellStopLoss = 9
    ModifiedSellTakeProfit = 10
    ClosedBuy = 11
    ClosedSell = 12
    BarClosed = 13
    AskAboveTarget = 14
    AskBelowTarget = 15
    BidAboveTarget = 16
    BidBelowTarget = 17
    Shutdown = 18

@dataclass(slots=True)
class CompleteUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI

@dataclass(slots=True)
class AccountUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Account: Account

@dataclass(slots=True)
class SymbolUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Symbol: Symbol

@dataclass(slots=True)
class PositionUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: Bar
    Account: Account
    Position: Position

@dataclass(slots=True)
class TradeUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: Bar
    Account: Account
    Trade: Trade

@dataclass(slots=True)
class PositionTradeUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: Bar
    Account: Account
    Position: Position
    Trade: Trade

@dataclass(slots=True)
class BarUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: Bar

@dataclass(slots=True)
class TickUpdate(Class):
    from Library.Robots.Analyst import AnalystAPI
    from Library.Robots.Manager import ManagerAPI
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Tick: Tick

Update = Union[
    CompleteUpdate,
    AccountUpdate,
    SymbolUpdate,
    PositionUpdate,
    TradeUpdate,
    PositionTradeUpdate,
    BarUpdate,
    TickUpdate
]
