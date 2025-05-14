from enum import Enum
from typing import Union
from attrs import define, field

from Agents.Analyst.Analyst import AnalystAPI
from Agents.Manager.Manager import ManagerAPI
from Agents.Container.Classes import Account, Symbol, Position, Trade, Bar, Tick

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

@define(slots=True)
class CompleteUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()

@define(slots=True)
class AccountUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Account: Account = field()

@define(slots=True)
class SymbolUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Symbol: Symbol = field()

@define(slots=True)
class PositionUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Bar: Bar = field()
    Account: Account = field()
    Position: Position = field()

@define(slots=True)
class TradeUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Bar: Bar = field()
    Account: Account = field()
    Trade: Trade = field()

@define(slots=True)
class PositionTradeUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Bar: Bar = field()
    Account: Account = field()
    Position: Position = field()
    Trade: Trade = field()

@define(slots=True)
class BarUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Bar: Bar = field()

@define(slots=True)
class TickUpdate:
    Analyst: AnalystAPI = field()
    Manager: ManagerAPI = field()
    Tick: Tick = field()
    
Update = Union[CompleteUpdate, AccountUpdate, SymbolUpdate, PositionUpdate, TradeUpdate, PositionTradeUpdate, BarUpdate, TickUpdate]