from abc import ABC, abstractmethod

from Agents.Logging.Console import ConsoleAPI
from Agents.Logging.Telegram import TelegramAPI
from Agents.Engine.Machine import MachineAPI
from Agents.Container.Updates import AccountUpdate, SymbolUpdate, PositionUpdate, TradeUpdate, PositionTradeUpdate, BarUpdate
from Agents.Parameters.Parameters import Parameters

class StrategyAPI(ABC):
    
    CONSOLE_OPENED_BUY = "Opened Buy ({0} Position)"
    CONSOLE_OPENED_SELL = "Opened Sell ({0} Position)"
    CONSOLE_MODIFIED_VOLUME_BUY = "Modified Buy Volume ({0} Position)"
    CONSOLE_MODIFIED_VOLUME_SELL = "Modified Sell Volume ({0} Position)"
    CONSOLE_MODIFIED_STOPLOSS_BUY = "Modified Buy Stop-Loss ({0} Position)"
    CONSOLE_MODIFIED_STOPLOSS_SELL = "Modified Sell Stop-Loss ({0} Position)"
    CONSOLE_MODIFIED_TAKEPROFIT_BUY = "Modified Buy Take-Profit ({0} Position)"
    CONSOLE_MODIFIED_TAKEPROFIT_SELL = "Modified Sell Take-Profit ({0} Position)"
    CONSOLE_CLOSED_BUY = "Closed Buy ({0} Position)"
    CONSOLE_CLOSED_SELL = "Closed Sell ({0} Position)"

    TELEGRAM_OPENED_BUY = "Opened Buy ({0} Position)"
    TELEGRAM_OPENED_SELL = "Opened Sell ({0} Position)"
    TELEGRAM_MODIFIED_VOLUME_BUY = "Modified Buy Volume ({0} Position)"
    TELEGRAM_MODIFIED_VOLUME_SELL = "Modified Sell Volume ({0} Position)"
    TELEGRAM_MODIFIED_STOPLOSS_BUY = "Modified Buy Stop-Loss ({0} Position)"
    TELEGRAM_MODIFIED_STOPLOSS_SELL = "Modified Sell Stop-Loss ({0} Position)"
    TELEGRAM_MODIFIED_TAKEPROFIT_BUY = "Modified Buy Take-Profit ({0} Position)"
    TELEGRAM_MODIFIED_TAKEPROFIT_SELL = "Modified Sell Take-Profit ({0} Position)"
    TELEGRAM_CLOSED_BUY = "Closed Buy ({0} Position)"
    TELEGRAM_CLOSED_SELL = "Closed Sell ({0} Position)"
    
    def __init__(self, money_management: Parameters, risk_management: Parameters, signal_management: Parameters):
        self.MoneyManagement: Parameters = money_management
        self.RiskManagement: Parameters = risk_management
        self.SignalManagement: Parameters = signal_management

        self._console: ConsoleAPI = ConsoleAPI(class_name=self.__class__.__name__, role_name="Strategy Management")
        self._telegram: TelegramAPI = TelegramAPI(class_name=self.__class__.__name__, role_name="Strategy Management")

    def _log_opened_buy(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_OPENED_BUY.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_OPENED_BUY.format(update.Position.PositionType.name))

    def _log_opened_sell(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_OPENED_SELL.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_OPENED_SELL.format(update.Position.PositionType.name))

    def _log_modified_volume_buy(self, update: PositionTradeUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_VOLUME_BUY.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_VOLUME_BUY.format(update.Position.PositionType.name))

    def _log_modified_volume_sell(self, update: PositionTradeUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_VOLUME_SELL.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_VOLUME_SELL.format(update.Position.PositionType.name))

    def _log_modified_stop_loss_buy(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_STOPLOSS_BUY.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_STOPLOSS_BUY.format(update.Position.PositionType.name))

    def _log_modified_stop_loss_sell(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_STOPLOSS_SELL.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_STOPLOSS_SELL.format(update.Position.PositionType.name))

    def _log_modified_take_profit_buy(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_TAKEPROFIT_BUY.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_TAKEPROFIT_BUY.format(update.Position.PositionType.name))

    def _log_modified_take_profit_sell(self, update: PositionUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_MODIFIED_TAKEPROFIT_SELL.format(update.Position.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_MODIFIED_TAKEPROFIT_SELL.format(update.Position.PositionType.name))

    def _log_closed_buy(self, update: TradeUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_CLOSED_BUY.format(update.Trade.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_CLOSED_BUY.format(update.Trade.PositionType.name))

    def _log_closed_sell(self, update: TradeUpdate):
        self._console.alert(lambda: StrategyAPI.CONSOLE_CLOSED_SELL.format(update.Trade.PositionType.name))
        self._telegram.alert(lambda: StrategyAPI.TELEGRAM_CLOSED_SELL.format(update.Trade.PositionType.name))
    
    @abstractmethod
    def risk_management(self) -> MachineAPI | None:
        raise NotImplementedError

    @abstractmethod
    def signal_management(self) -> MachineAPI | None:
        raise NotImplementedError

    def strategy_management(self) -> MachineAPI | None:

        strategy_engine = MachineAPI("Strategy Management")

        initialisation = strategy_engine.create_state(name="Initialisation", end=False)
        execution = strategy_engine.create_state(name="Execution", end=False)
        termination = strategy_engine.create_state(name="Termination", end=True)

        def init_account(update: AccountUpdate):
            update.Manager.Account.init_account(update.Account)

        def init_symbol(update: SymbolUpdate):
            update.Manager.Symbol.init_symbol(update.Symbol)

        def update_bar(update: BarUpdate):
            update.Manager.Symbol.update_symbol(update.Bar)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
        
        def update_opened_buy(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.open_position_buy(update.Account, update.Position)
            self._log_opened_buy(update)

        def update_opened_sell(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.open_position_sell(update.Account, update.Position)
            self._log_opened_sell(update)

        def update_modified_buy_volume(update: PositionTradeUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_trade_buy(update.Position, update.Trade)
            update.Manager.Statistics.update_data(update.Trade)
            self._log_modified_volume_buy(update)

        def update_modified_buy_stop_loss(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_buy(update.Position)
            self._log_modified_stop_loss_buy(update)

        def update_modified_buy_take_profit(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_buy(update.Position)
            self._log_modified_take_profit_buy(update)

        def update_modified_sell_volume(update: PositionTradeUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_trade_sell(update.Position, update.Trade)
            update.Manager.Statistics.update_data(update.Trade)
            self._log_modified_volume_sell(update)

        def update_modified_sell_stop_loss(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_sell(update.Position)
            self._log_modified_stop_loss_sell(update)

        def update_modified_sell_take_profit(update: PositionUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.modify_position_sell(update.Position)
            self._log_modified_take_profit_sell(update)

        def update_closed_buy(update: TradeUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.close_position_buy(update.Trade)
            update.Manager.Statistics.update_data(update.Trade)
            self._log_closed_buy(update)

        def update_closed_sell(update: TradeUpdate):
            update.Manager.Account.update_account(update.Account)
            update.Manager.Positions.update_position(update.Bar, update.Manager.Symbol.PipSize)
            update.Manager.Positions.close_position_sell(update.Trade)
            update.Manager.Statistics.update_data(update.Trade)
            self._log_closed_sell(update)

        initialisation.on_account(to=initialisation, action=init_account, reason="Account Initialized")
        initialisation.on_symbol(to=initialisation, action=init_symbol, reason="Symbol Initialized")
        initialisation.on_complete(to=execution, action=None, reason="Initialized")
        initialisation.on_shutdown(to=termination, action=None, reason="Abruptly Terminated")

        execution.on_bar_closed(to=execution, action=update_bar, reason=None)
        execution.on_opened_buy(to=execution, action=update_opened_buy, reason="Opened Buy Position")
        execution.on_opened_sell(to=execution, action=update_opened_sell, reason="Opened Sell Position")
        execution.on_modified_volume_buy(to=execution, action=update_modified_buy_volume, reason="Modified Buy Volume")
        execution.on_modified_stop_loss_buy(to=execution, action=update_modified_buy_stop_loss, reason="Modified Buy Stop-Loss")
        execution.on_modified_take_profit_buy(to=execution, action=update_modified_buy_take_profit, reason="Modified Buy Take-Profit")
        execution.on_modified_volume_sell(to=execution, action=update_modified_sell_volume, reason="Modified Sell Volume")
        execution.on_modified_stop_loss_sell(to=execution, action=update_modified_sell_stop_loss, reason="Modified Sell Stop-Loss")
        execution.on_modified_take_profit_sell(to=execution, action=update_modified_sell_take_profit, reason="Modified Sell Take-Profit")
        execution.on_closed_buy(to=execution, action=update_closed_buy, reason="Closed Buy Position")
        execution.on_closed_sell(to=execution, action=update_closed_sell, reason="Closed Sell Position")
        execution.on_shutdown(to=termination, action=None, reason="Safely Terminated")

        return strategy_engine
