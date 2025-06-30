from enum import Enum
from typing import Union
from attrs import define, field

from Library.Classes import PositionType

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

@define(slots=True)
class CompleteAction:
    ActionID: ActionID = field(default=ActionID.Complete, init=False)

@define(slots=True)
class OpenBuyAction:
    ActionID: ActionID = field(default=ActionID.OpenBuy, init=False)
    PositionType: PositionType = field(converter=PositionType)
    Volume: float = field(converter=float)
    StopLoss: float | None = field(converter=lambda x: None if x is None else float(x))
    TakeProfit: float | None = field(converter=lambda x: None if x is None else float(x))

@define(slots=True)
class OpenSellAction:
    ActionID: ActionID = field(default=ActionID.OpenSell, init=False)
    PositionType: PositionType = field(converter=PositionType)
    Volume: float = field(converter=float)
    StopLoss: float | None = field(converter=lambda x: None if x is None else float(x))
    TakeProfit: float | None = field(converter=lambda x: None if x is None else float(x))

@define(slots=True)
class ModifyBuyVolumeAction:
    ActionID: ActionID = field(default=ActionID.ModifyBuyVolume, init=False)
    PositionID: int = field(converter=int)
    Volume: float = field(converter=float)

@define(slots=True)
class ModifySellVolumeAction:
    ActionID: ActionID = field(default=ActionID.ModifySellVolume, init=False)
    PositionID: int = field(converter=int)
    Volume: float = field(converter=float)

@define(slots=True)
class ModifyBuyStopLossAction:
    ActionID: ActionID = field(default=ActionID.ModifyBuyStopLoss, init=False)
    PositionID: int = field(converter=int)
    StopLoss: float = field(converter=float)

@define(slots=True)
class ModifySellStopLossAction:
    ActionID: ActionID = field(default=ActionID.ModifySellStopLoss, init=False)
    PositionID: int = field(converter=int)
    StopLoss: float = field(converter=float)

@define(slots=True)
class ModifyBuyTakeProfitAction:
    ActionID: ActionID = field(default=ActionID.ModifyBuyTakeProfit, init=False)
    PositionID: int = field(converter=int)
    TakeProfit: float = field(converter=float)

@define(slots=True)
class ModifySellTakeProfitAction:
    ActionID: ActionID = field(default=ActionID.ModifySellTakeProfit, init=False)
    PositionID: int = field(converter=int)
    TakeProfit: float = field(converter=float)

@define(slots=True)
class CloseBuyAction:
    ActionID: ActionID = field(default=ActionID.CloseBuy, init=False)
    PositionID: int = field(converter=int)

@define(slots=True)
class CloseSellAction:
    ActionID: ActionID = field(default=ActionID.CloseSell, init=False)
    PositionID: int = field(converter=int)

@define(slots=True)
class AskAboveTargetAction:
    ActionID: ActionID = field(default=ActionID.AskAboveTarget, init=False)
    Ask: float | None = field(converter=lambda x: None if x is None else float(x))

@define(slots=True)
class AskBelowTargetAction:
    ActionID: ActionID = field(default=ActionID.AskBelowTarget, init=False)
    Ask: float | None = field(converter=lambda x: None if x is None else float(x))

@define(slots=True)
class BidAboveTargetAction:
    ActionID: ActionID = field(default=ActionID.BidAboveTarget, init=False)
    Bid: float | None = field(converter=lambda x: None if x is None else float(x))

@define(slots=True)
class BidBelowTargetAction:
    ActionID: ActionID = field(default=ActionID.BidBelowTarget, init=False)
    Bid: float | None = field(converter=lambda x: None if x is None else float(x))
    
Action = Union[CompleteAction, OpenBuyAction, OpenSellAction, ModifyBuyVolumeAction, ModifyBuyStopLossAction,
               ModifyBuyTakeProfitAction, ModifySellVolumeAction, ModifySellStopLossAction, ModifySellTakeProfitAction,
               CloseBuyAction, CloseSellAction, AskAboveTargetAction, AskBelowTargetAction, BidAboveTargetAction, BidBelowTargetAction]