import polars as pl

from datetime import date, datetime
from itertools import count
from queue import Queue
from typing import Type, Iterator, Callable

from Library.Robots.Database.Database import DatabaseAPI
from Library.Robots.Analyst.Analyst import AnalystAPI
from Library.Robots.Manager.Manager import ManagerAPI
from Library.Robots.Engine.Machine import MachineAPI
from Library.Robots.Container.Enums import AssetType, PositionType, TradeType
from Library.Robots.Container.Classes import Account, Symbol, Position, Bar, Tick, Trade
from Library.Robots.Container.Actions import ActionID, CompleteAction
from Library.Robots.Container.Actions import OpenBuyAction, OpenSellAction
from Library.Robots.Container.Actions import ModifyBuyVolumeAction, ModifyBuyStopLossAction, ModifyBuyTakeProfitAction
from Library.Robots.Container.Actions import ModifySellVolumeAction, ModifySellStopLossAction, ModifySellTakeProfitAction
from Library.Robots.Container.Actions import CloseBuyAction, CloseSellAction
from Library.Robots.Container.Actions import AskAboveTargetAction, AskBelowTargetAction, BidAboveTargetAction, BidBelowTargetAction
from Library.Robots.Container.Updates import UpdateID, CompleteUpdate, BarUpdate
from Library.Robots.Strategy.Strategy import StrategyAPI
from Library.Robots.System.System import SystemAPI
from Library.Robots.Parameters.Parameters import ParametersAPI, Parameters
from Library.Robots.Utils.Performance import time

class BacktestingAPI(SystemAPI):

    watchlist = ParametersAPI().Watchlist
    TICK = watchlist.Timeframes[0]
    SYMBOLS = [symbol for group in watchlist.Symbols.values() for symbol in group]

    tick_data: pl.DataFrame | None = None
    bar_data: pl.DataFrame | None = None
    symbol_data: Symbol | None = None
    conversion_data: pl.DataFrame | None = None
    conversion_rate: Callable[[datetime], float] | None = None
    window: int | None = None

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 strategy: Type[StrategyAPI],
                 parameters: Parameters,
                 start: str | date,
                 stop: str | date,
                 balance: float,
                 spread: float):

        super().__init__(broker=broker, group=group, symbol=symbol, timeframe=timeframe, strategy=strategy, parameters=parameters)

        def parse_date(x: str | date) -> (str, date):
            if isinstance(x, str):
                return x, datetime.strptime(x, "%d-%m-%Y").date()
            else:
                return x.strftime("%d-%m-%Y"), x

        self._start_str, self._start_date = parse_date(start)
        self._stop_str, self._stop_date = parse_date(stop)

        self._initial_account: Account = Account(balance, balance)
        self._account: Account = Account(balance, balance)
        self._spread_pips: float = spread
        self._spread_price: float | None = None

        self._tick_db: DatabaseAPI | None = None
        self._tick_data_iterator: Iterator | None = None
        self._tick_data_next: Bar | None = None
        self._tick_open_next: Tick | None = None

        self._bar_db: DatabaseAPI | None = None
        self._bar_data_iterator: Iterator | None = None
        self._bar_data_at: Bar | None = None
        self._bar_data_at_last: Bar | None = None
        self._bar_data_next: Bar | None = None

        self._conversion_db: DatabaseAPI | None = None

        self._offset: int | None = None

        self._update_id_queue: Queue[UpdateID] = Queue()
        self._update_args_queue: Queue[Account | Symbol | Position | Trade | Bar | Tick] = Queue()

        self._pids: count = count(start=1)
        self._tids: count = count(start=1)
        self._positions: dict[int, Position] = {}
        self._ask_above_target: float | None = None
        self._ask_below_target: float | None = None
        self._bid_above_target: float | None = None
        self._bid_below_target: float | None = None

    def __enter__(self):
        if self.strategy is None:
            self.strategy = self._strategy(money_management=self._parameters.MoneyManagement, risk_management=self._parameters.RiskManagement, signal_management=self._parameters.SignalManagement)

        if self.analyst is None:
            self.analyst = AnalystAPI(analyst_management=self._parameters.AnalystManagement)

        if self.manager is None:
            self.manager = ManagerAPI(manager_management=self._parameters.ManagerManagement)

        if self.window is None:
            self.window = self.analyst.Window

        if self.tick_data is None:
            self._tick_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=self._symbol, timeframe=self.TICK)
            self._tick_db.__enter__()
            self.tick_data = self._tick_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
        self._tick_data_iterator = self.tick_data.iter_rows()
        self._tick_data_next = Bar(*next(self._tick_data_iterator))

        if self.bar_data is None:
            self._bar_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=self._symbol, timeframe=self._timeframe)
            self._bar_db.__enter__()
            self.bar_data = self._bar_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=self.window)
        self._bar_data_iterator = self.bar_data.filter((pl.col(DatabaseAPI.MARKET_TIMESTAMP) >= self._start_date) & (pl.col(DatabaseAPI.MARKET_TIMESTAMP) <= self._stop_date)).iter_rows()
        start_bar_data_index = Bar(*self.bar_data.row(self.window))
        self._bar_data_at = Bar(*next(self._bar_data_iterator))
        self._bar_data_next = Bar(*next(self._bar_data_iterator))
        while self._bar_data_at.Timestamp < start_bar_data_index.Timestamp:
            self._bar_data_at = self._bar_data_next
            self._bar_data_next = Bar(*next(self._bar_data_iterator))
        self._bar_data_at_last = Bar(self._bar_data_at.Timestamp, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, 0.0)
        self._offset = self.bar_data.height - self.window + 1

        if self.symbol_data is None:
            self.symbol_data: Symbol = self._bar_db.pull_symbol_data()
        self._spread_price = self._spread_pips * self.symbol_data.PipSize

        if self.conversion_data is None or self.conversion_rate is None:
            current_rate = lambda timestamp: self.conversion_data.filter(pl.col(DatabaseAPI.MARKET_TIMESTAMP) <= timestamp).tail(1).select(DatabaseAPI.MARKET_OPENPRICE).item()
            if self.symbol_data.BaseAsset == AssetType.EUR:
                self._conversion_db = self._tick_db
                self.conversion_data = self.tick_data
                self.conversion_rate = lambda timestamp: 1.0 / (current_rate(timestamp) + self._spread_price)
            elif (symbol := f"{AssetType.EUR.name}{self.symbol_data.QuoteAsset.name}") in self.SYMBOLS:
                self._conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                self._conversion_db.__enter__()
                self.conversion_data = self._conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                self.conversion_rate = lambda timestamp: 1.0 / (current_rate(timestamp) + self._spread_price)
            elif (symbol := f"{self.symbol_data.QuoteAsset.name}{AssetType.EUR.name}") in self.SYMBOLS:
                self._conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                self._conversion_db.__enter__()
                self.conversion_data = self._conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                self.conversion_rate = lambda timestamp: current_rate(timestamp)
            else:
                self.conversion_data = self.tick_data
                self.conversion_rate = lambda timestamp: 1.0

        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._tick_db:
            self._tick_db.__exit__(None, None, None)
        if self._bar_db:
            self._bar_db.__exit__(None, None, None)
        if self._conversion_db:
            self._conversion_db.__exit__(None, None, None)
        return super().__exit__(exc_type, exc_value, exc_traceback)

    def _calculate_ask_bid(self, price: float) -> (float, float):
        return price + self._spread_price, price

    def _update_position(self, pid: int, position: Position) -> None:
        self._positions[pid] = position

    def _delete_position(self, pid: int) -> None:
        del self._positions[pid]

    def _find_position(self, pid: int) -> Position | None:
        return self._positions[pid] if pid in self._positions else None

    def _next_pid(self):
        next(self._tids)
        return next(self._pids)

    def _next_tid(self):
        return next(self._tids)

    def _open_buy_position(self, position_type: PositionType, volume: float, sl_price_delta: float | None, tp_price_delta: float | None, tick: Tick) -> Position:
        pid = self._next_pid()
        entry_time = tick.Timestamp
        entry_price = tick.Ask
        sl_price = None if sl_price_delta is None else entry_price - sl_price_delta
        tp_price = None if tp_price_delta is None else entry_price + tp_price_delta
        return Position(pid, position_type, TradeType.Buy, entry_time, entry_price, volume, sl_price, tp_price)

    def _open_sell_position(self, position_type: PositionType, volume: float, sl_price_delta: float | None, tp_price_delta: float | None, tick: Tick) -> Position:
        pid = self._next_pid()
        entry_time = tick.Timestamp
        entry_price = tick.Bid
        sl_price = None if sl_price_delta is None else entry_price + sl_price_delta
        tp_price = None if tp_price_delta is None else entry_price - tp_price_delta
        return Position(pid, position_type, TradeType.Sell, entry_time, entry_price, volume, sl_price, tp_price)

    def _close_buy_position(self, position: Position, tick: Tick) -> Trade:
        tid = self._next_tid()
        exit_time = tick.Timestamp
        exit_price = tick.Bid
        price_delta = exit_price - position.EntryPrice
        gross_pnl = price_delta * position.Volume * self.conversion_rate(tick.Timestamp)
        commission_pnl = 0.0
        swap_pnl = 0.0
        net_pips = price_delta / self.symbol_data.PipSize
        net_pnl = gross_pnl - commission_pnl - swap_pnl
        return Trade(position.PositionID, tid, position.PositionType, position.TradeType, position.EntryTimestamp, exit_time, position.EntryPrice, exit_price, position.Volume, gross_pnl, commission_pnl, swap_pnl, net_pips, net_pnl)

    def _close_sell_position(self, position: Position, tick: Tick) -> Trade:
        tid = self._next_tid()
        exit_time = tick.Timestamp
        exit_price = tick.Ask
        price_delta = position.EntryPrice - exit_price 
        gross_pnl = price_delta * position.Volume * self.conversion_rate(tick.Timestamp)
        commission_pnl = 0.0
        swap_pnl = 0.0
        net_pips = price_delta / self.symbol_data.PipSize
        net_pnl = gross_pnl - commission_pnl - swap_pnl
        return Trade(position.PositionID, tid, position.PositionType, position.TradeType, position.EntryTimestamp, exit_time, position.EntryPrice, exit_price, position.Volume, gross_pnl, commission_pnl, swap_pnl, net_pips, net_pnl)

    def send_action_complete(self, action: CompleteAction) -> None:
        pass

    def send_action_open(self, action: OpenBuyAction | OpenSellAction) -> None:
        if action.Volume > self.symbol_data.VolumeInUnitsMax:
            return self._console.error(lambda: f"Action Open: Invalid Volume above the maximum units ({action.Volume})")
        if action.Volume < self.symbol_data.VolumeInUnitsMin:
            return self._console.error(lambda: f"Action Open: Invalid Volume below the minimum units ({action.Volume})")
        if action.Volume % self.symbol_data.VolumeInUnitsStep != 0.0:
            return self._console.error(lambda: f"Action Open: Invalid Volume not normalised to minimum step ({action.Volume})")
        if action.StopLoss:
            action.StopLoss = action.StopLoss * self.symbol_data.PipSize
            if action.StopLoss < self.symbol_data.TickSize:
                self._console.error(lambda: f"Action Open: Invalid Stop Loss below the minimum tick ({action.StopLoss})")
                action.StopLoss = None
        if action.TakeProfit:
            action.TakeProfit = action.TakeProfit * self.symbol_data.PipSize
            if action.TakeProfit < self.symbol_data.TickSize:
                self._console.error(lambda: f"Action Open: Invalid Take Profit below the minimum tick ({action.TakeProfit})")
                action.TakeProfit = None

        update_id: UpdateID | None = None
        position: Position | None = None
        match action.ActionID:
            case ActionID.OpenBuy:
                update_id = UpdateID.OpenedBuy
                position = self._open_buy_position(action.PositionType, action.Volume, action.StopLoss, action.TakeProfit, self._tick_open_next)
            case ActionID.OpenSell:
                update_id = UpdateID.OpenedSell
                position = self._open_sell_position(action.PositionType, action.Volume, action.StopLoss, action.TakeProfit, self._tick_open_next)

        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account)
        self._update_args_queue.put(position)
        self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_volume(self, action: ModifyBuyVolumeAction | ModifySellVolumeAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._console.error(lambda: "Action Modify Volume: Position not found")
        if action.Volume == position.Volume:
            return self._console.error(lambda: f"Action Modify Volume: Invalid new Volume equal to old Volume ({action.Volume})")
        if action.Volume > self.symbol_data.VolumeInUnitsMax:
            return self._console.error(lambda: f"Action Modify Volume: Invalid Volume above the maximum units ({action.Volume})")
        if action.Volume < self.symbol_data.VolumeInUnitsMin:
            return self._console.error(lambda: f"Action Modify Volume: Invalid Volume below the minimum units ({action.Volume})")
        if action.Volume % self.symbol_data.VolumeInUnitsStep != 0.0:
            return self._console.error(lambda: f"Action Modify Volume: Invalid Volume not normalised to minimum step ({action.Volume})")

        update_id: UpdateID | None = None
        trade: Trade | None = None
        match action.ActionID:
            case ActionID.ModifyBuyVolume:
                if action.Volume == 0.0:
                    self._console.warning(lambda: f"Action Modify Volume: Closing Buy position as Volume is zero")
                    return self.send_action_close(CloseBuyAction(action.PositionID))
                update_id = UpdateID.ModifiedBuyVolume
                position.Volume = position.Volume - action.Volume
                trade = self._close_buy_position(position, self._tick_open_next)
                position.Volume = action.Volume
            case ActionID.ModifySellVolume:
                if action.Volume == 0.0:
                    self._console.warning(lambda: f"Action Modify Volume: Closing Sell position as Volume is zero")
                    return self.send_action_close(CloseSellAction(action.PositionID))
                update_id = UpdateID.ModifiedSellVolume
                position.Volume = position.Volume - action.Volume
                trade = self._close_sell_position(position, self._tick_open_next)
                position.Volume = action.Volume
            
        self._account.Balance += trade.NetPnL
        self._account.Equity += trade.NetPnL
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account)
        self._update_args_queue.put(position)
        self._update_args_queue.put(trade)
        self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_stop_loss(self, action: ModifyBuyStopLossAction | ModifySellStopLossAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._console.error(lambda: "Action Modify Stop Loss: Position not found")
        if action.StopLoss == position.StopLoss:
            return self._console.error(lambda: f"Action Modify Stop Loss: Invalid new Stop Loss equal to old Stop Loss ({action.StopLoss})")
        if action.StopLoss:
            action.StopLoss = action.StopLoss

        update_id: UpdateID | None = None
        match action.ActionID:
            case ActionID.ModifyBuyStopLoss:
                if action.StopLoss > self._tick_open_next.Bid:
                    return self._console.error(lambda: f"Action Modify Stop Loss: Invalid Buy Stop Loss above to the Bid Price ({action.StopLoss})")
                update_id = UpdateID.ModifiedBuyStopLoss
            case ActionID.ModifySellStopLoss:
                if action.StopLoss < self._tick_open_next.Ask:
                    return self._console.error(lambda: f"Action Modify Stop Loss: Invalid Sell Stop Loss below the Ask Price ({action.StopLoss})")
                update_id = UpdateID.ModifiedSellStopLoss

        position.StopLoss = action.StopLoss
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account)
        self._update_args_queue.put(position)
        self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_take_profit(self, action: ModifyBuyTakeProfitAction | ModifySellTakeProfitAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._console.error(lambda: "Action Modify Take Profit: Position not found")
        if action.TakeProfit == position.TakeProfit:
            return self._console.error(lambda: f"Action Modify Take Profit: Invalid new Take Profit equal to old Take Profit ({action.TakeProfit})")
        if action.TakeProfit:
            action.TakeProfit = action.TakeProfit

        update_id: UpdateID | None = None
        match action.ActionID:
            case ActionID.ModifyBuyTakeProfit:
                if action.TakeProfit < self._tick_open_next.Bid:
                    return self._console.error(lambda: f"Action Modify Take Profit: Invalid Buy Take Profit below the Bid Price ({action.TakeProfit})")
                update_id = UpdateID.ModifiedBuyTakeProfit
            case ActionID.ModifySellTakeProfit:
                if action.TakeProfit > self._tick_open_next.Ask:
                    return self._console.error(lambda: f"Action Modify Take Profit: Invalid Sell Take Profit above the Entry Price ({action.TakeProfit})")
                update_id = UpdateID.ModifiedSellTakeProfit

        position.TakeProfit = action.TakeProfit
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account)
        self._update_args_queue.put(position)
        self._update_id_queue.put(UpdateID.Complete)

    def send_action_close(self, action: CloseBuyAction | CloseSellAction, tick: Tick = None) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._console.error(lambda: "Action Close: Position not found")

        update_id: UpdateID | None = None
        trade: Trade | None = None
        match action.ActionID:
            case action.ActionID.CloseBuy:
                update_id = UpdateID.ClosedBuy
                trade = self._close_buy_position(position, self._tick_open_next if not tick else tick)
            case action.ActionID.CloseSell:
                update_id = UpdateID.ClosedSell
                trade = self._close_sell_position(position, self._tick_open_next if not tick else tick)

        self._account.Balance += trade.NetPnL
        self._account.Equity += trade.NetPnL
        self._delete_position(position.PositionID)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account)
        self._update_args_queue.put(trade)
        self._update_id_queue.put(UpdateID.Complete)

    def send_action_ask_above_target(self, action: AskAboveTargetAction) -> None:
        self._ask_above_target = action.Ask

    def send_action_ask_below_target(self, action: AskBelowTargetAction) -> None:
        self._ask_below_target = action.Ask

    def send_action_bid_above_target(self, action: BidAboveTargetAction) -> None:
        self._bid_above_target = action.Bid

    def send_action_bid_below_target(self, action: BidBelowTargetAction) -> None:
        self._bid_below_target = action.Bid

    def receive_update_id(self) -> UpdateID:

        while self._bar_data_next or self._tick_data_next or not self._update_id_queue.empty():

            if not self._update_id_queue.empty():
                return self._update_id_queue.get()

            if self._bar_data_next and self._tick_data_next.Timestamp >= self._bar_data_next.Timestamp:

                self._update_id_queue.put(UpdateID.BarClosed)
                self._update_args_queue.put(self._bar_data_at)
                self._update_id_queue.put(UpdateID.Complete)

                self._bar_data_at = self._bar_data_next
                self._bar_data_at_last.Timestamp = self._bar_data_at.Timestamp
                self._bar_data_at_last.OpenPrice = self._bar_data_at_last.HighPrice = self._bar_data_at_last.LowPrice = self._bar_data_at_last.ClosePrice = self._bar_data_at.OpenPrice
                self._bar_data_at_last.TickVolume = 0.0
                try:
                    self._bar_data_next = Bar(*next(self._bar_data_iterator))
                except StopIteration:
                    self._bar_data_next = None
                continue

            if self._tick_data_next:
                
                high_ask_at, high_bid_at = self._calculate_ask_bid(self._tick_data_next.HighPrice)
                low_ask_at, low_bid_at = self._calculate_ask_bid(self._tick_data_next.LowPrice)
                
                self._bar_data_at_last.HighPrice = max(self._bar_data_at_last.HighPrice, self._tick_data_next.HighPrice)
                self._bar_data_at_last.LowPrice = min(self._bar_data_at_last.LowPrice, self._tick_data_next.LowPrice)
                self._bar_data_at_last.ClosePrice = self._tick_data_next.ClosePrice
                self._bar_data_at_last.TickVolume += self._tick_data_next.TickVolume

                try:
                    self._tick_data_next = Bar(*next(self._tick_data_iterator))
                    self._tick_open_next = Tick(self._tick_data_next.Timestamp, *self._calculate_ask_bid(self._tick_data_next.OpenPrice))
                except StopIteration:
                    self._tick_data_next = None

                for position_id, position in list(self._positions.items()):
                    match position.TradeType:
                        case TradeType.Buy:
                            if position.StopLoss is not None:
                                if low_bid_at <= position.StopLoss:
                                    self.send_action_close(CloseBuyAction(position_id), Tick(self._tick_open_next.Timestamp, low_ask_at, low_bid_at))
                                    continue
                                if self._tick_open_next.Bid <= position.StopLoss:
                                    self.send_action_close(CloseBuyAction(position_id))
                                    continue
                            if position.TakeProfit is not None:
                                if high_bid_at >= position.TakeProfit:
                                    self.send_action_close(CloseBuyAction(position_id), Tick(self._tick_open_next.Timestamp, high_ask_at, high_bid_at))
                                    continue
                                if self._tick_open_next.Bid >= position.TakeProfit:
                                    self.send_action_close(CloseBuyAction(position_id))
                                    continue
                        case TradeType.Sell:
                            if position.StopLoss is not None:
                                if high_ask_at >= position.StopLoss:
                                    self.send_action_close(CloseSellAction(position_id), Tick(self._tick_open_next.Timestamp, high_ask_at, high_bid_at))
                                    continue
                                if self._tick_open_next.Ask >= position.StopLoss:
                                    self.send_action_close(CloseSellAction(position_id))
                                    continue
                            if position.TakeProfit is not None:
                                if low_ask_at <= position.TakeProfit:
                                    self.send_action_close(CloseSellAction(position_id), Tick(self._tick_open_next.Timestamp, low_ask_at, low_bid_at))
                                    continue
                                if self._tick_open_next.Ask <= position.TakeProfit:
                                    self.send_action_close(CloseSellAction(position_id))
                                    continue

                if self._ask_above_target is not None and self._tick_open_next.Ask >= self._ask_above_target:
                    self._ask_above_target = None
                    self._update_id_queue.put(UpdateID.AskAboveTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._ask_below_target is not None and self._tick_open_next.Ask <= self._ask_below_target:
                    self._ask_below_target = None
                    self._update_id_queue.put(UpdateID.AskBelowTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._bid_above_target is not None and self._tick_open_next.Bid >= self._bid_above_target:
                    self._bid_above_target = None
                    self._update_id_queue.put(UpdateID.BidAboveTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._bid_below_target is not None and self._tick_open_next.Bid <= self._bid_below_target:
                    self._bid_below_target = None
                    self._update_id_queue.put(UpdateID.BidBelowTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

        return UpdateID.Shutdown

    def receive_update_account(self) -> Account:
        return self._update_args_queue.get()

    def receive_update_symbol(self) -> Symbol:
        return self._update_args_queue.get()

    def receive_update_position(self) -> Position:
        return self._update_args_queue.get()

    def receive_update_trade(self) -> Trade:
        return self._update_args_queue.get()

    def receive_update_bar(self) -> Bar:
        return self._update_args_queue.get()

    def receive_update_target(self) -> Tick:
        return self._update_args_queue.get()

    def system_management(self) -> MachineAPI:

        system_engine = MachineAPI("System Management")

        initialisation = system_engine.create_state(name="Initialisation", end=False)
        execution = system_engine.create_state(name="Execution", end=False)
        termination = system_engine.create_state(name="Termination", end=True)

        def init_market(update: CompleteUpdate):
            update.Analyst.init_market_data(self.bar_data)
            update.Analyst.update_market_offset(self._offset)

        def update_market(update: BarUpdate):
            self._offset -= 1
            update.Analyst.update_market_offset(self._offset)

        def update_results(update: CompleteUpdate):
            self.individual_trades, self.aggregated_trades, self.statistics = update.Manager.Statistics.data(self._initial_account, self._start_date, self._stop_date)
            self._console.debug(lambda: str(self.individual_trades))
            self._console.debug(lambda: str(self.aggregated_trades))
            self._console.debug(lambda: str(self.statistics))

        initialisation.on_complete(to=execution, action=init_market, reason="Market Initialized")
        initialisation.on_shutdown(to=termination, action=None, reason="Abruptly Terminated")

        execution.on_bar_closed(to=execution, action=update_market, reason=None)
        execution.on_shutdown(to=termination, action=update_results, reason="Safely Terminated")

        return system_engine

    @time
    def run(self) -> None:
        self._update_id_queue.put(UpdateID.Account)
        self._update_args_queue.put(self._initial_account)

        self._update_id_queue.put(UpdateID.Symbol)
        self._update_args_queue.put(self.symbol_data)

        self._update_id_queue.put(UpdateID.Complete)

        self.deploy(strategy=self.strategy, analyst=self.analyst, manager=self.manager)
