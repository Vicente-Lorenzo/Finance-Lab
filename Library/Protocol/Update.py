from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

from Library.Utility.Dataclass import DataclassAPI
from Library.Portfolio.Account import AccountAPI
from Library.Universe.Symbol import SymbolAPI
from Library.Portfolio.Position import PositionAPI
from Library.Portfolio.Trade import TradeAPI
from Library.Market.Bar import BarAPI
from Library.Market.Tick import TickAPI

if TYPE_CHECKING:
    from Library.Analyst import AnalystAPI
    from Library.Manager import ManagerAPI

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
class CompleteUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI

@dataclass(slots=True)
class AccountUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Account: AccountAPI

@dataclass(slots=True)
class SymbolUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Symbol: SymbolAPI

@dataclass(slots=True)
class PositionUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: BarAPI
    Account: AccountAPI
    Position: PositionAPI

@dataclass(slots=True)
class TradeUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: BarAPI
    Account: AccountAPI
    Trade: TradeAPI

@dataclass(slots=True)
class PositionTradeUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: BarAPI
    Account: AccountAPI
    Position: PositionAPI
    Trade: TradeAPI

@dataclass(slots=True)
class BarUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Bar: BarAPI

@dataclass(slots=True)
class TickUpdate(DataclassAPI):
    Analyst: AnalystAPI
    Manager: ManagerAPI
    Tick: TickAPI

Update = CompleteUpdate | AccountUpdate | SymbolUpdate | PositionUpdate | TradeUpdate | PositionTradeUpdate | BarUpdate | TickUpdate
