import polars as pl

from typing import Type
from abc import abstractmethod
from threading import Thread

from Library.Robots.Logging.Console import ConsoleAPI
from Library.Robots.Logging.Telegram import TelegramAPI
from Library.Robots.Analyst.Analyst import AnalystAPI
from Agents.Manager.Manager import ManagerAPI
from Agents.Engine.Machine import MachineAPI
from Agents.Engine.Engine import EngineAPI
from Agents.Container.Classes import Account, Symbol, Position, Trade, Bar, Tick
from Agents.Container.Actions import ActionID, CompleteAction
from Agents.Container.Actions import OpenBuyAction, OpenSellAction
from Agents.Container.Actions import ModifyBuyVolumeAction, ModifyBuyStopLossAction, ModifyBuyTakeProfitAction
from Agents.Container.Actions import ModifySellVolumeAction, ModifySellStopLossAction, ModifySellTakeProfitAction
from Agents.Container.Actions import CloseBuyAction, CloseSellAction
from Agents.Container.Actions import AskAboveTargetAction, AskBelowTargetAction, BidAboveTargetAction, BidBelowTargetAction
from Agents.Container.Updates import UpdateID, CompleteUpdate, AccountUpdate, SymbolUpdate, PositionUpdate, TradeUpdate, PositionTradeUpdate, BarUpdate, TickUpdate
from Agents.Strategy.Strategy import StrategyAPI
from Agents.Parameters.Parameters import Parameters

class SystemAPI(Thread):

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 strategy: Type[StrategyAPI],
                 parameters: Parameters):
        
        super().__init__(daemon=True)

        self._broker: str = broker
        self._group: str = group
        self._symbol: str = symbol
        self._timeframe: str = timeframe
        
        self._strategy: Type[StrategyAPI] = strategy
        
        self._parameters: Parameters = parameters

        self.strategy: StrategyAPI | None = None
        self.analyst: AnalystAPI | None = None
        self.manager: ManagerAPI | None = None
        
        self.individual_trades: pl.DataFrame | None = None
        self.aggregated_trades: pl.DataFrame | None = None
        self.statistics: pl.DataFrame | None = None

        self._console: ConsoleAPI = ConsoleAPI(class_name=self.__class__.__name__, role_name="System Management")
        self._telegram: TelegramAPI = TelegramAPI(class_name=self.__class__.__name__, role_name="System Management")
    
    def __enter__(self):
        self._console.info(lambda: "Initiated")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._console.info(lambda: "Terminated")
        if exc_type or exc_value or exc_traceback:
            self._console.critical(lambda: f"Exception type: {exc_type}")
            self._console.critical(lambda: f"Exception value: {exc_value}")
            self._console.critical(lambda: f"Traceback: {exc_traceback}")
    
    @abstractmethod
    def send_action_complete(self, action: CompleteAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_open(self, action: OpenBuyAction | OpenSellAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_modify_volume(self, action: ModifyBuyVolumeAction | ModifySellVolumeAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_modify_stop_loss(self, action: ModifyBuyStopLossAction | ModifySellStopLossAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_modify_take_profit(self, action: ModifyBuyTakeProfitAction | ModifySellTakeProfitAction) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def send_action_close(self, action: CloseBuyAction | CloseSellAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_ask_above_target(self, action: AskAboveTargetAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_ask_below_target(self, action: AskBelowTargetAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_bid_above_target(self, action: BidAboveTargetAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_bid_below_target(self, action: BidBelowTargetAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def receive_update_id(self) -> UpdateID:
        raise NotImplementedError

    @abstractmethod
    def receive_update_account(self) -> Account:
        raise NotImplementedError

    @abstractmethod
    def receive_update_symbol(self) -> Symbol:
        raise NotImplementedError

    @abstractmethod
    def receive_update_position(self) -> Position:
        raise NotImplementedError

    @abstractmethod
    def receive_update_trade(self) -> Trade:
        raise NotImplementedError

    @abstractmethod
    def receive_update_bar(self) -> Bar:
        raise NotImplementedError

    @abstractmethod
    def receive_update_target(self) -> Tick:
        raise NotImplementedError

    @abstractmethod
    def system_management(self) -> MachineAPI:
        raise NotImplementedError

    def deploy(self, strategy: StrategyAPI, analyst: AnalystAPI, manager: ManagerAPI) -> None:
        system = EngineAPI(system_engine=self.system_management(),
                           strategy_management=strategy.strategy_management(),
                           signal_engine=strategy.signal_management(),
                           risk_engine=strategy.risk_management())
        while not system.is_terminated():
            actions = []
            while True:
                update_id = self.receive_update_id()
                match update_id:
                    case UpdateID.Complete:
                        actions += system.perform_update_complete(CompleteUpdate(analyst, manager))
                        break
                    case UpdateID.Account:
                        actions += system.perform_update_account(AccountUpdate(analyst, manager, self.receive_update_account()))
                    case UpdateID.Symbol:
                        actions += system.perform_update_symbol(SymbolUpdate(analyst, manager, self.receive_update_symbol()))
                    case UpdateID.OpenedBuy:
                        actions += system.perform_update_opened_buy(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.OpenedSell:
                        actions += system.perform_update_opened_sell(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.ModifiedBuyVolume:
                        actions += system.perform_update_modified_volume_buy(PositionTradeUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position(), self.receive_update_trade()))
                    case UpdateID.ModifiedBuyStopLoss:
                        actions += system.perform_update_modified_stop_loss_buy(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.ModifiedBuyTakeProfit:
                        actions += system.perform_update_modified_take_profit_buy(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.ModifiedSellVolume:
                        actions += system.perform_update_modified_volume_sell(PositionTradeUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position(), self.receive_update_trade()))
                    case UpdateID.ModifiedSellStopLoss:
                        actions += system.perform_update_modified_stop_loss_sell(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.ModifiedSellTakeProfit:
                        actions += system.perform_update_modified_take_profit_sell(PositionUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_position()))
                    case UpdateID.ClosedBuy:
                        actions += system.perform_update_closed_buy(TradeUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_trade()))
                    case UpdateID.ClosedSell:
                        actions += system.perform_update_closed_sell(TradeUpdate(analyst, manager, self.receive_update_bar(), self.receive_update_account(), self.receive_update_trade()))
                    case UpdateID.BarClosed:
                        actions += system.perform_update_bar_closed(BarUpdate(analyst, manager, self.receive_update_bar()))
                    case UpdateID.AskAboveTarget:
                        actions += system.perform_update_ask_above_target(TickUpdate(analyst, manager, self.receive_update_target()))
                    case UpdateID.AskBelowTarget:
                        actions += system.perform_update_ask_below_target(TickUpdate(analyst, manager, self.receive_update_target()))
                    case UpdateID.BidAboveTarget:
                        actions += system.perform_update_bid_above_target(TickUpdate(analyst, manager, self.receive_update_target()))
                    case UpdateID.BidBelowTarget:
                        actions += system.perform_update_bid_below_target(TickUpdate(analyst, manager, self.receive_update_target()))
                    case UpdateID.Shutdown:
                        self._console.warning(lambda: "Shutdown strategy and safely terminate operations")
                        actions += system.perform_update_shutdown(CompleteUpdate(analyst, manager))
                        break
                    case _:
                        self._console.error(lambda: f"Received invalid update ID: {update_id}")
                        raise
            for action in actions:
                match action.ActionID:
                    case ActionID.Complete:
                        self.send_action_complete(action)
                    case ActionID.OpenBuy | ActionID.OpenSell:
                        self.send_action_open(action)
                    case ActionID.ModifyBuyVolume | ActionID.ModifySellVolume:
                        self.send_action_modify_volume(action)
                    case ActionID.ModifyBuyStopLoss | ActionID.ModifySellStopLoss:
                        self.send_action_modify_stop_loss(action)
                    case ActionID.ModifyBuyTakeProfit | ActionID.ModifySellTakeProfit:
                        self.send_action_modify_take_profit(action)
                    case ActionID.CloseBuy | ActionID.CloseSell:
                        self.send_action_close(action)
                    case ActionID.AskAboveTarget:
                        self.send_action_ask_above_target(action)
                    case ActionID.AskBelowTarget:
                        self.send_action_ask_below_target(action)
                    case ActionID.BidAboveTarget:
                        self.send_action_bid_above_target(action)
                    case ActionID.BidBelowTarget:
                        self.send_action_bid_below_target(action)
                    case _:
                        self._console.error(lambda: f"Sent invalid action ID: {action.ActionID}")
                        raise
            self.send_action_complete(CompleteAction())
                    
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError
