from typing import Callable

from Library.Robots.Container.Actions import Action
from Library.Robots.Container.Updates import Update, CompleteUpdate, AccountUpdate, SymbolUpdate, PositionUpdate, TradeUpdate, PositionTradeUpdate, BarUpdate, TickUpdate
from Library.Robots.Engine.Machine import MachineAPI

class EngineAPI:
    
    def __init__(self, system_engine: MachineAPI = None, strategy_management: MachineAPI = None, signal_engine: MachineAPI = None, risk_engine: MachineAPI = None):
        self._system_engine: MachineAPI = system_engine or self._create_dummy_engine()
        self._strategy_management: MachineAPI = strategy_management or self._create_dummy_engine()
        self._signal_engine: MachineAPI = signal_engine or self._create_dummy_engine()
        self._risk_engine: MachineAPI = risk_engine or self._create_dummy_engine()
        
    @staticmethod
    def _create_dummy_engine() -> MachineAPI:
        engine = MachineAPI(None)
        execution = engine.create_state(None, False)
        termination = engine.create_state(None, True)
        execution.on_shutdown(to=termination, action=None, reason="Safely Terminated")
        return engine

    @staticmethod
    def _perform_update(system_update_function: Callable[[Update], list[Action]],
                        strategy_update_function: Callable[[Update], list[Action]],
                        signal_update_function: Callable[[Update], list[Action]],
                        risk_update_function: Callable[[Update], list[Action]],
                        update_args) -> list[Action]:
        system_engine_return = system_update_function(update_args)
        strategy_engine_return = strategy_update_function(update_args)
        signal_engine_return = signal_update_function(update_args)
        risk_engine_return = risk_update_function(update_args)
        if system_engine_return:
            return system_engine_return
        if strategy_engine_return:
            return strategy_engine_return
        if signal_engine_return:
            return signal_engine_return
        if risk_engine_return:
            return risk_engine_return
        return []
    
    def is_terminated(self) -> bool:
        return self._system_engine.at.end and self._strategy_management.at.end and self._signal_engine.at.end and self._risk_engine.at.end

    def perform_update_shutdown(self, args: CompleteUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_shutdown, self._strategy_management.perform_update_shutdown, self._signal_engine.perform_update_shutdown, self._risk_engine.perform_update_shutdown, args)

    def perform_update_complete(self, args: CompleteUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_complete, self._strategy_management.perform_update_complete, self._signal_engine.perform_update_complete, self._risk_engine.perform_update_complete, args)

    def perform_update_account(self, args: AccountUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_account, self._strategy_management.perform_update_account, self._signal_engine.perform_update_account, self._risk_engine.perform_update_account, args)

    def perform_update_symbol(self, args: SymbolUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_symbol, self._strategy_management.perform_update_symbol, self._signal_engine.perform_update_symbol, self._risk_engine.perform_update_symbol, args)

    def perform_update_opened_buy(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_opened_buy, self._strategy_management.perform_update_opened_buy, self._signal_engine.perform_update_opened_buy, self._risk_engine.perform_update_opened_buy, args)

    def perform_update_opened_sell(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_opened_sell, self._strategy_management.perform_update_opened_sell, self._signal_engine.perform_update_opened_sell, self._risk_engine.perform_update_opened_sell, args)

    def perform_update_modified_volume_buy(self, args: PositionTradeUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_volume_buy, self._strategy_management.perform_update_modified_volume_buy, self._signal_engine.perform_update_modified_volume_buy, self._risk_engine.perform_update_modified_volume_buy, args)

    def perform_update_modified_stop_loss_buy(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_stop_loss_buy, self._strategy_management.perform_update_modified_stop_loss_buy, self._signal_engine.perform_update_modified_stop_loss_buy, self._risk_engine.perform_update_modified_stop_loss_buy, args)

    def perform_update_modified_take_profit_buy(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_take_profit_buy, self._strategy_management.perform_update_modified_take_profit_buy, self._signal_engine.perform_update_modified_take_profit_buy, self._risk_engine.perform_update_modified_take_profit_buy, args)

    def perform_update_modified_volume_sell(self, args: PositionTradeUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_volume_sell, self._strategy_management.perform_update_modified_volume_sell, self._signal_engine.perform_update_modified_volume_sell, self._risk_engine.perform_update_modified_volume_sell, args)

    def perform_update_modified_stop_loss_sell(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_stop_loss_sell, self._strategy_management.perform_update_modified_stop_loss_sell, self._signal_engine.perform_update_modified_stop_loss_sell, self._risk_engine.perform_update_modified_stop_loss_sell, args)

    def perform_update_modified_take_profit_sell(self, args: PositionUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_modified_take_profit_sell, self._strategy_management.perform_update_modified_take_profit_sell, self._signal_engine.perform_update_modified_take_profit_sell, self._risk_engine.perform_update_modified_take_profit_sell, args)

    def perform_update_closed_buy(self, args: TradeUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_closed_buy, self._strategy_management.perform_update_closed_buy, self._signal_engine.perform_update_closed_buy, self._risk_engine.perform_update_closed_buy, args)

    def perform_update_closed_sell(self, args: TradeUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_closed_sell, self._strategy_management.perform_update_closed_sell, self._signal_engine.perform_update_closed_sell, self._risk_engine.perform_update_closed_sell, args)

    def perform_update_bar_closed(self, args: BarUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_bar_closed, self._strategy_management.perform_update_bar_closed, self._signal_engine.perform_update_bar_closed, self._risk_engine.perform_update_bar_closed, args)

    def perform_update_ask_above_target(self, args: TickUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_ask_above_target, self._strategy_management.perform_update_ask_above_target, self._signal_engine.perform_update_ask_above_target, self._risk_engine.perform_update_ask_above_target, args)

    def perform_update_ask_below_target(self, args: TickUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_ask_below_target, self._strategy_management.perform_update_ask_below_target, self._signal_engine.perform_update_ask_below_target, self._risk_engine.perform_update_ask_below_target, args)

    def perform_update_bid_above_target(self, args: TickUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_bid_above_target, self._strategy_management.perform_update_bid_above_target, self._signal_engine.perform_update_bid_above_target, self._risk_engine.perform_update_bid_above_target, args)

    def perform_update_bid_below_target(self, args: TickUpdate) -> list[Action]:
        return self._perform_update(self._system_engine.perform_update_bid_below_target, self._strategy_management.perform_update_bid_below_target, self._signal_engine.perform_update_bid_below_target, self._risk_engine.perform_update_bid_below_target, args)
