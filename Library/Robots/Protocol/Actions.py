from enum import Enum
from typing import Union
from dataclasses import dataclass, field
from Library.Classes import PositionType, Class

class ActionID(Enum):
    Complete = 0
    OpenBuy = 1
    OpenSell = 2
    ModifyBuyVolume = 3
    ModifyBuyStopLoss = 4
    ModifyBuyTakeProfit = 5
    ModifySellVolume = 6
    ModifySellStopLoss = 7
    ModifySellTakeProfit = 8
    CloseBuy = 9
    CloseSell = 10
    AskAboveTarget = 11
    AskBelowTarget = 12
    BidAboveTarget = 13
    BidBelowTarget = 14

@dataclass(slots=True)
class CompleteAction(Class):
    ActionID: ActionID = field(default=ActionID.Complete, init=False)

@dataclass(slots=True)
class OpenBuyAction(Class):
    ActionID: ActionID = field(default=ActionID.OpenBuy, init=False)
    PositionType: PositionType
    Volume: float
    StopLoss: float | None
    TakeProfit: float | None

    def __post_init__(self):
        self.PositionType = PositionType(self.PositionType)
        self.StopLoss = None if self.StopLoss is None else float(self.StopLoss)
        self.TakeProfit = None if self.TakeProfit is None else float(self.TakeProfit)

@dataclass(slots=True)
class OpenSellAction(Class):
    ActionID: ActionID = field(default=ActionID.OpenSell, init=False)
    PositionType: PositionType
    Volume: float
    StopLoss: float | None
    TakeProfit: float | None

    def __post_init__(self):
        self.PositionType = PositionType(self.PositionType)
        self.StopLoss = None if self.StopLoss is None else float(self.StopLoss)
        self.TakeProfit = None if self.TakeProfit is None else float(self.TakeProfit)

@dataclass(slots=True)
class ModifyBuyVolumeAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifyBuyVolume, init=False)
    PositionID: int
    Volume: float

@dataclass(slots=True)
class ModifySellVolumeAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifySellVolume, init=False)
    PositionID: int
    Volume: float

@dataclass(slots=True)
class ModifyBuyStopLossAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifyBuyStopLoss, init=False)
    PositionID: int
    StopLoss: float | None

@dataclass(slots=True)
class ModifySellStopLossAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifySellStopLoss, init=False)
    PositionID: int
    StopLoss: float | None

@dataclass(slots=True)
class ModifyBuyTakeProfitAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifyBuyTakeProfit, init=False)
    PositionID: int
    TakeProfit: float | None

@dataclass(slots=True)
class ModifySellTakeProfitAction(Class):
    ActionID: ActionID = field(default=ActionID.ModifySellTakeProfit, init=False)
    PositionID: int
    TakeProfit: float | None

@dataclass(slots=True)
class CloseBuyAction(Class):
    ActionID: ActionID = field(default=ActionID.CloseBuy, init=False)
    PositionID: int

@dataclass(slots=True)
class CloseSellAction(Class):
    ActionID: ActionID = field(default=ActionID.CloseSell, init=False)
    PositionID: int

@dataclass(slots=True)
class AskAboveTargetAction(Class):
    ActionID: ActionID = field(default=ActionID.AskAboveTarget, init=False)
    Ask: float | None

    def __post_init__(self):
        self.Ask = None if self.Ask is None else float(self.Ask)

@dataclass(slots=True)
class AskBelowTargetAction(Class):
    ActionID: ActionID = field(default=ActionID.AskBelowTarget, init=False)
    Ask: float | None

    def __post_init__(self):
        self.Ask = None if self.Ask is None else float(self.Ask)

@dataclass(slots=True)
class BidAboveTargetAction(Class):
    ActionID: ActionID = field(default=ActionID.BidAboveTarget, init=False)
    Bid: float | None

    def __post_init__(self):
        self.Bid = None if self.Bid is None else float(self.Bid)

@dataclass(slots=True)
class BidBelowTargetAction(Class):
    ActionID: ActionID = field(default=ActionID.BidBelowTarget, init=False)
    Bid: float | None

    def __post_init__(self):
        self.Bid = None if self.Bid is None else float(self.Bid)

Action = Union[
    CompleteAction,
    OpenBuyAction,
    OpenSellAction,
    ModifyBuyVolumeAction,
    ModifyBuyStopLossAction,
    ModifyBuyTakeProfitAction,
    ModifySellVolumeAction,
    ModifySellStopLossAction,
    ModifySellTakeProfitAction,
    CloseBuyAction,
    CloseSellAction,
    AskAboveTargetAction,
    AskBelowTargetAction,
    BidAboveTargetAction,
    BidBelowTargetAction
]
