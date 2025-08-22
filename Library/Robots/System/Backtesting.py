import copy
import polars as pl

from datetime import date, datetime
from itertools import count
from queue import Queue
from typing import Type, Iterator, Callable

from Library.Classes import *
from Library.Database import DatabaseAPI
from Library.Parameters import ParametersAPI, Parameters
from Library.Utils import timer, datetime_to_string, string_to_datetime

from Library.Robots.Protocol import *
from Library.Robots.Analyst import AnalystAPI
from Library.Robots.Manager import ManagerAPI
from Library.Robots.Engine import MachineAPI
from Library.Robots.Strategy import StrategyAPI
from Library.Robots.System import SystemAPI

class BacktestingSystemAPI(SystemAPI):

    watchlist = ParametersAPI().Watchlist
    TICK = watchlist.Timeframes[0]
    SYMBOLS = [symbol for group in watchlist.Symbols.values() for symbol in group]

    account_data: Account | None = None

    tick_db: DatabaseAPI | None = None
    tick_data: pl.DataFrame | None = None

    bar_db: DatabaseAPI | None = None
    bar_data: pl.DataFrame | None = None

    symbol_data: Symbol | None = None

    base_conversion_db: DatabaseAPI | None = None
    base_conversion_data: pl.DataFrame | None = None
    base_conversion_rate: Callable[[datetime, float], float] | None = None

    quote_conversion_db: DatabaseAPI | None = None
    quote_conversion_data: pl.DataFrame | None = None
    quote_conversion_rate: Callable[[datetime, float], float] | None = None

    spread_fee_rate: Callable[[datetime, float], float] | None = None
    commission_fee_rate: Callable[[datetime, float], float] | None = None
    swap_buy_fee_rate: Callable[[datetime, float], float] | None = None
    swap_sell_fee_rate: Callable[[datetime, float], float] | None = None

    window: int | None = None
    offset: int | None = None

    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 strategy: Type[StrategyAPI],
                 parameters: Parameters,
                 start: str | date,
                 stop: str | date,
                 account: tuple[AssetType, float, float],
                 spread: tuple[SpreadType, float],
                 commission: tuple[CommissionType, float],
                 swap: tuple[SwapType, float, float]):

        super().__init__(broker=broker, group=group, symbol=symbol, timeframe=timeframe, strategy=strategy, parameters=parameters)

        def parse_date(x: str | date) -> tuple[str | date, str | date]:
            if isinstance(x, str):
                return x, string_to_datetime(x, "%d-%m-%Y").date()
            else:
                return datetime_to_string(x, "%d-%m-%Y"), x

        self._start_str, self._start_date = parse_date(start)
        self._stop_str, self._stop_date = parse_date(stop)

        self._account_asset, self._account_balance, self._account_leverage = account
        self._account_data: Account | None = None

        self._spread_type, self._spread_value = spread
        self._commission_type, self._commission_value = commission
        self._swap_type, self._swap_buy, self._swap_sell  = swap

        self._tick_data_iterator: Iterator | None = None
        self._tick_data_next: Bar | None = None
        self._tick_open_next: Tick | None = None

        self._bar_data_iterator: Iterator | None = None
        self._bar_data_at: Bar | None = None
        self._bar_data_at_last: Bar | None = None
        self._bar_data_next: Bar | None = None

        self._offset: int | None = None

        self._update_id_queue: Queue[UpdateID] | None = None
        self._update_args_queue: Queue[Account | Symbol | Position | Trade | Bar | Tick] | None = None

        self._pids: count = count(start=1)
        self._tids: count = count(start=1)
        self._positions: dict[int, Position] = {}
        self._ask_above_target: float | None = None
        self._ask_below_target: float | None = None
        self._bid_above_target: float | None = None
        self._bid_below_target: float | None = None

    def __enter__(self):
        if self.strategy is None:
            self.strategy = self._strategy(money_management=self.parameters.MoneyManagement, risk_management=self.parameters.RiskManagement, signal_management=self.parameters.SignalManagement)

        if self.analyst is None:
            self.analyst = AnalystAPI(analyst_management=self.parameters.AnalystManagement)

        if self.manager is None:
            self.manager = ManagerAPI(manager_management=self.parameters.ManagerManagement)

        if self.window is None:
            self.window = self.analyst.Window

        if self.account_data is None:
            self.account_data: Account = Account(
                AccountType=AccountType.Hedged,
                AssetType=self._account_asset,
                Balance=self._account_balance,
                Equity=self._account_balance,
                Credit=0.0,
                Leverage=self._account_leverage,
                MarginUsed=0.0,
                MarginFree=self._account_balance,
                MarginLevel=None,
                MarginStopLevel=50.0,
                MarginMode=MarginMode.Max
            )
        self._account_data: Account = copy.deepcopy(self.account_data)

        if self.tick_data is None:
            self.tick_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=self._symbol, timeframe=self.TICK)
            self.tick_db.__enter__()
            self.tick_data = self.tick_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
        self._tick_data_iterator = self.tick_data.iter_rows()
        self._tick_data_next = Bar(*next(self._tick_data_iterator))
        self._tick_open_next = None

        if self.bar_data is None:
            self.bar_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=self._symbol, timeframe=self._timeframe)
            self.bar_db.__enter__()
            self.bar_data = self.bar_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=self.window)
            self.offset = self.bar_data.height - self.window + 1
        self._offset = self.offset
        self._bar_data_iterator = self.bar_data.filter((pl.col(DatabaseAPI.MARKET_TIMESTAMP) >= self._start_date) & (pl.col(DatabaseAPI.MARKET_TIMESTAMP) <= self._stop_date)).iter_rows()
        start_bar_data_index = Bar(*self.bar_data.row(self.window))
        self._bar_data_at = Bar(*next(self._bar_data_iterator))
        self._bar_data_next = Bar(*next(self._bar_data_iterator))
        while self._bar_data_at.Timestamp < start_bar_data_index.Timestamp:
            self._bar_data_at = self._bar_data_next
            self._bar_data_next = Bar(*next(self._bar_data_iterator))
        self._bar_data_at_last = Bar(self._bar_data_at.Timestamp, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, self._bar_data_at.OpenPrice, 0.0)

        if self.symbol_data is None:
            self.symbol_data: Symbol = self.bar_db.pull_symbol_data()

        if self.base_conversion_data is None or self.base_conversion_rate is None or self.quote_conversion_data is None or self.quote_conversion_rate is None:
            base_rate = lambda timestamp: self.base_conversion_data.filter(pl.col(DatabaseAPI.MARKET_TIMESTAMP) <= timestamp).tail(1).select(DatabaseAPI.MARKET_OPENPRICE).item()
            quote_rate = lambda timestamp: self.quote_conversion_data.filter(pl.col(DatabaseAPI.MARKET_TIMESTAMP) <= timestamp).tail(1).select(DatabaseAPI.MARKET_OPENPRICE).item()

            self.base_conversion_db = self.tick_db
            self.base_conversion_data = self.tick_db
            self.base_conversion_rate = lambda timestamp, spread: 1.0

            self.quote_conversion_db = self.tick_db
            self.quote_conversion_data = self.tick_data
            self.quote_conversion_rate = lambda timestamp, spread: 1.0

            if self.account_data.AssetType == self.symbol_data.BaseAssetType:
                self.quote_conversion_db = self.tick_db
                self.quote_conversion_data = self.tick_data
                self.quote_conversion_rate = lambda timestamp, spread: 1.0 / (quote_rate(timestamp) + spread)
            elif self.account_data.AssetType == self.symbol_data.QuoteAssetType:
                self.base_conversion_db = self.tick_db
                self.base_conversion_data = self.tick_db
                self.base_conversion_rate = lambda timestamp, spread: 1.0 / (base_rate(timestamp) + spread)
            else:
                if (symbol := f"{self.account_data.AssetType.name}{self.symbol_data.BaseAssetType.name}") in self.SYMBOLS:
                    self.base_conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                    self.base_conversion_db.__enter__()
                    self.base_conversion_data = self.base_conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                    self.base_conversion_rate = lambda timestamp, spread: 1.0 / (base_rate(timestamp) + spread)
                elif (symbol := f"{self.symbol_data.BaseAssetType.name}{self.account_data.AssetType.name}") in self.SYMBOLS:
                    self.base_conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                    self.base_conversion_db.__enter__()
                    self.base_conversion_data = self.base_conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                    self.base_conversion_rate = lambda timestamp, spread: base_rate(timestamp)
                else:
                    self._log.error(lambda: f"Base Asset to Account Asset convertion formula not found")

                if (symbol := f"{self.account_data.AssetType.name}{self.symbol_data.QuoteAssetType.name}") in self.SYMBOLS:
                    self.quote_conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                    self.quote_conversion_db.__enter__()
                    self.quote_conversion_data = self.quote_conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                    self.quote_conversion_rate = lambda timestamp, spread: 1.0 / (quote_rate(timestamp) + spread)
                elif (symbol := f"{self.symbol_data.QuoteAssetType.name}{self.account_data.AssetType.name}") in self.SYMBOLS:
                    self.quote_conversion_db = DatabaseAPI(broker=self._broker, group=self._group, symbol=symbol, timeframe=self.TICK)
                    self.quote_conversion_db.__enter__()
                    self.quote_conversion_data = self.quote_conversion_db.pull_market_data(start=self._start_str, stop=self._stop_str, window=None)
                    self.quote_conversion_rate = lambda timestamp, spread: quote_rate(timestamp)
                else:
                    self._log.error(lambda: f"Quote Asset to Account Asset convertion formula not found")

        if self.spread_fee_rate is None:
            match self._spread_type:
                case SpreadType.Points:
                    self.spread_fee_rate = lambda timestamp, price: self._spread_value * self.symbol_data.PointSize
                case SpreadType.Pips:
                    self.spread_fee_rate = lambda timestamp, price: self._spread_value * self.symbol_data.PipSize
                case SpreadType.Percentage:
                    self.spread_fee_rate = lambda timestamp, price: (self._spread_value / 100) * price
                case SpreadType.Accurate:
                    raise NotImplementedError

        if self.commission_fee_rate is None:
            match self._commission_type:
                case CommissionType.Points:
                    pass # raise NotImplementedError
                case CommissionType.Pips:
                    pass # raise NotImplementedError
                case CommissionType.Percentage:
                    pass # raise NotImplementedError
                case CommissionType.Amount:
                    pass # raise NotImplementedError
                case CommissionType.Accurate:
                    match self.symbol_data.CommissionMode:
                        case CommissionMode.BaseAssetPerMillionVolume:
                            self.commission_fee_rate = lambda timestamp, spread: (self.symbol_data.Commission / 1_000_000) * self.base_conversion_rate(timestamp, spread)
                        case CommissionMode.BaseAssetPerOneLot:
                            self.commission_fee_rate = lambda timestamp, spread: (self.symbol_data.Commission / self.symbol_data.LotSize) * self.base_conversion_rate(timestamp, spread)
                        case CommissionMode.PercentageOfVolume:
                            pass
                        case CommissionMode.QuoteAssetPerOneLot:
                            pass

        if self.swap_buy_fee_rate is None or self.swap_sell_fee_rate is None:
            match self._swap_type:
                case SwapType.Points:
                    pass # raise NotImplementedError
                case SwapType.Pips:
                    pass # raise NotImplementedError
                case SwapType.Percentage:
                    pass # raise NotImplementedError
                case SwapType.Amount:
                    pass # raise NotImplementedError
                case SwapType.Accurate:
                    raise NotImplementedError

        self._update_id_queue = Queue()
        self._update_args_queue = Queue()

        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.tick_db:
            self.tick_db.__exit__(None, None, None)
        if self.bar_db:
            self.bar_db.__exit__(None, None, None)
        if self.quote_conversion_db:
            self.quote_conversion_db.__exit__(None, None, None)
        return super().__exit__(exc_type, exc_value, exc_traceback)

    def _calculate_ask_bid(self, timestamp: datetime, price: float) -> tuple[float, float]:
        return price + self.spread_fee_rate(timestamp, price), price

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

    def _calculate_metrics(self, volume: float, price_delta: float, tick: Tick) -> tuple[float, float, float, float, float, float, float, float]:
        quantity = volume / self.symbol_data.LotSize
        points = price_delta / self.symbol_data.PointSize
        pips = price_delta / self.symbol_data.PipSize
        gross_pnl = price_delta * volume * self.quote_conversion_rate(tick.Timestamp, tick.Spread)
        commission_pnl = - volume * self.commission_fee_rate(tick.Timestamp, tick.Spread)
        swap_pnl = 0.0
        net_pnl = gross_pnl + commission_pnl + swap_pnl
        used_margin = 0.0
        return quantity, points, pips, gross_pnl, commission_pnl, swap_pnl, net_pnl, used_margin

    def _open_position(self, position_type: PositionType, trade_type: TradeType, volume: float, entry_price: float, sl_price: float | None, tp_price: float | None, price_delta: float, tick: Tick) -> Position:
        pid = self._next_pid()
        entry_time = tick.Timestamp
        quantity, points, pips, gross_pnl, commission_pnl, swap_pnl, net_pnl, used_margin = self._calculate_metrics(volume, price_delta, tick)
        return Position(
            PositionID=pid,
            PositionType=position_type,
            TradeType=trade_type,
            EntryTimestamp=entry_time,
            EntryPrice=entry_price,
            Volume=volume,
            Quantity=quantity,
            Points=points,
            Pips=pips,
            GrossPnL=gross_pnl,
            CommissionPnL=commission_pnl,
            SwapPnL=swap_pnl,
            NetPnL=net_pnl,
            StopLoss=sl_price,
            TakeProfit=tp_price,
            UsedMargin=used_margin
        )

    def _open_buy_position(self, position_type: PositionType, volume: float, sl_price_delta: float | None, tp_price_delta: float | None, tick: Tick) -> Position:
        entry_price = tick.Ask
        sl_price = None if sl_price_delta is None else entry_price - sl_price_delta
        tp_price = None if tp_price_delta is None else entry_price + tp_price_delta
        price_delta = tick.Bid - entry_price
        return self._open_position(position_type, TradeType.Buy, volume, entry_price, sl_price, tp_price, price_delta, tick)

    def _open_sell_position(self, position_type: PositionType, volume: float, sl_price_delta: float | None, tp_price_delta: float | None, tick: Tick) -> Position:
        entry_price = tick.Bid
        sl_price = None if sl_price_delta is None else entry_price + sl_price_delta
        tp_price = None if tp_price_delta is None else entry_price - tp_price_delta
        price_delta = entry_price - tick.Ask
        return self._open_position(position_type, TradeType.Sell, volume, entry_price, sl_price, tp_price, price_delta, tick)

    def _close_position(self, position: Position, exit_price: float, price_delta: float, tick: Tick) -> Trade:
        tid = self._next_tid()
        exit_time = tick.Timestamp
        quantity, points, pips, gross_pnl, commission_pnl, swap_pnl, net_pnl, used_margin = self._calculate_metrics(position.Volume, price_delta, tick)
        return Trade(
            PositionID=position.PositionID,
            TradeID=tid,
            PositionType=position.PositionType,
            TradeType=position.TradeType,
            EntryTimestamp=position.EntryTimestamp,
            ExitTimestamp=exit_time,
            EntryPrice=position.EntryPrice,
            ExitPrice=exit_price,
            Volume=position.Volume,
            Quantity=quantity,
            Points=points,
            Pips=pips,
            GrossPnL=gross_pnl,
            CommissionPnL=position.CommissionPnL+commission_pnl,
            SwapPnL=swap_pnl,
            NetPnL=net_pnl
        )

    def _close_buy_position(self, position: Position, tick: Tick) -> Trade:
        exit_price = tick.Bid
        price_delta = exit_price - position.EntryPrice
        return self._close_position(position, exit_price, price_delta, tick)

    def _close_sell_position(self, position: Position, tick: Tick) -> Trade:
        exit_price = tick.Ask
        price_delta = position.EntryPrice - exit_price
        return self._close_position(position, exit_price, price_delta, tick)

    def send_action_complete(self, action: CompleteAction) -> None:
        pass

    def send_action_open(self, action: OpenBuyAction | OpenSellAction) -> None:
        if action.Volume > self.symbol_data.VolumeInUnitsMax:
            return self._log.error(lambda: f"Action Open: Invalid Volume above the maximum units ({action.Volume})")
        if action.Volume < self.symbol_data.VolumeInUnitsMin:
            return self._log.error(lambda: f"Action Open: Invalid Volume below the minimum units ({action.Volume})")
        if action.Volume % self.symbol_data.VolumeInUnitsStep != 0.0:
            return self._log.error(lambda: f"Action Open: Invalid Volume not normalised to minimum step ({action.Volume})")
        if action.StopLoss:
            action.StopLoss = action.StopLoss * self.symbol_data.PipSize
            if action.StopLoss < self.symbol_data.PointSize:
                self._log.error(lambda: f"Action Open: Invalid Stop Loss below the minimum tick ({action.StopLoss})")
                action.StopLoss = None
        if action.TakeProfit:
            action.TakeProfit = action.TakeProfit * self.symbol_data.PipSize
            if action.TakeProfit < self.symbol_data.PointSize:
                self._log.error(lambda: f"Action Open: Invalid Take Profit below the minimum tick ({action.TakeProfit})")
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
        self._update_args_queue.put(self._account_data)
        self._update_args_queue.put(position)
        return self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_volume(self, action: ModifyBuyVolumeAction | ModifySellVolumeAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._log.error(lambda: "Action Modify Volume: Position not found")
        if action.Volume == position.Volume:
            return self._log.error(lambda: f"Action Modify Volume: Invalid new Volume equal to old Volume ({action.Volume})")
        if action.Volume > self.symbol_data.VolumeInUnitsMax:
            return self._log.error(lambda: f"Action Modify Volume: Invalid Volume above the maximum units ({action.Volume})")
        if action.Volume < self.symbol_data.VolumeInUnitsMin:
            return self._log.error(lambda: f"Action Modify Volume: Invalid Volume below the minimum units ({action.Volume})")
        if action.Volume % self.symbol_data.VolumeInUnitsStep != 0.0:
            return self._log.error(lambda: f"Action Modify Volume: Invalid Volume not normalised to minimum step ({action.Volume})")

        update_id: UpdateID | None = None
        trade: Trade | None = None
        initial_volume: float = position.Volume
        initial_commission: float = position.CommissionPnL
        match action.ActionID:
            case ActionID.ModifyBuyVolume:
                if action.Volume == 0.0:
                    self._log.warning(lambda: f"Action Modify Volume: Closing Buy position as Volume is zero")
                    return self.send_action_close(CloseBuyAction(action.PositionID))
                update_id = UpdateID.ModifiedBuyVolume
                position.Volume = initial_volume - action.Volume
                position.CommissionPnL = initial_commission * (position.Volume / initial_volume)
                trade = self._close_buy_position(position, self._tick_open_next)
            case ActionID.ModifySellVolume:
                if action.Volume == 0.0:
                    self._log.warning(lambda: f"Action Modify Volume: Closing Sell position as Volume is zero")
                    return self.send_action_close(CloseSellAction(action.PositionID))
                update_id = UpdateID.ModifiedSellVolume
                position.Volume = initial_volume - action.Volume
                position.CommissionPnL = initial_commission * (position.Volume / initial_volume)
                trade = self._close_sell_position(position, self._tick_open_next)

        position.Volume = action.Volume
        position.CommissionPnL = initial_commission * (action.Volume / initial_volume)
        self._account_data.Balance += trade.NetPnL
        self._account_data.Equity += trade.NetPnL
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account_data)
        self._update_args_queue.put(position)
        self._update_args_queue.put(trade)
        return self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_stop_loss(self, action: ModifyBuyStopLossAction | ModifySellStopLossAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._log.error(lambda: "Action Modify Stop Loss: Position not found")
        if action.StopLoss == position.StopLoss:
            return self._log.error(lambda: f"Action Modify Stop Loss: Invalid new Stop Loss equal to old Stop Loss ({action.StopLoss})")
        if action.StopLoss:
            action.StopLoss = action.StopLoss

        update_id: UpdateID | None = None
        match action.ActionID:
            case ActionID.ModifyBuyStopLoss:
                if action.StopLoss > self._tick_open_next.Bid:
                    return self._log.error(lambda: f"Action Modify Stop Loss: Invalid Buy Stop Loss above to the Bid Price ({action.StopLoss})")
                update_id = UpdateID.ModifiedBuyStopLoss
            case ActionID.ModifySellStopLoss:
                if action.StopLoss < self._tick_open_next.Ask:
                    return self._log.error(lambda: f"Action Modify Stop Loss: Invalid Sell Stop Loss below the Ask Price ({action.StopLoss})")
                update_id = UpdateID.ModifiedSellStopLoss

        position.StopLoss = action.StopLoss
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account_data)
        self._update_args_queue.put(position)
        return self._update_id_queue.put(UpdateID.Complete)

    def send_action_modify_take_profit(self, action: ModifyBuyTakeProfitAction | ModifySellTakeProfitAction) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._log.error(lambda: "Action Modify Take Profit: Position not found")
        if action.TakeProfit == position.TakeProfit:
            return self._log.error(lambda: f"Action Modify Take Profit: Invalid new Take Profit equal to old Take Profit ({action.TakeProfit})")
        if action.TakeProfit:
            action.TakeProfit = action.TakeProfit

        update_id: UpdateID | None = None
        match action.ActionID:
            case ActionID.ModifyBuyTakeProfit:
                if action.TakeProfit < self._tick_open_next.Bid:
                    return self._log.error(lambda: f"Action Modify Take Profit: Invalid Buy Take Profit below the Bid Price ({action.TakeProfit})")
                update_id = UpdateID.ModifiedBuyTakeProfit
            case ActionID.ModifySellTakeProfit:
                if action.TakeProfit > self._tick_open_next.Ask:
                    return self._log.error(lambda: f"Action Modify Take Profit: Invalid Sell Take Profit above the Entry Price ({action.TakeProfit})")
                update_id = UpdateID.ModifiedSellTakeProfit

        position.TakeProfit = action.TakeProfit
        self._update_position(position.PositionID, position)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account_data)
        self._update_args_queue.put(position)
        return self._update_id_queue.put(UpdateID.Complete)

    def send_action_close(self, action: CloseBuyAction | CloseSellAction, tick: Tick = None) -> None:
        position: Position = self._find_position(action.PositionID)
        if not position:
            return self._log.error(lambda: "Action Close: Position not found")

        update_id: UpdateID | None = None
        trade: Trade | None = None
        match action.ActionID:
            case ActionID.CloseBuy:
                update_id = UpdateID.ClosedBuy
                trade = self._close_buy_position(position, self._tick_open_next if not tick else tick)
            case ActionID.CloseSell:
                update_id = UpdateID.ClosedSell
                trade = self._close_sell_position(position, self._tick_open_next if not tick else tick)

        self._account_data.Balance += trade.NetPnL
        self._account_data.Equity += trade.NetPnL
        self._delete_position(position.PositionID)
        self._update_id_queue.put(update_id)
        self._update_args_queue.put(self._bar_data_at_last)
        self._update_args_queue.put(self._account_data)
        self._update_args_queue.put(trade)
        return self._update_id_queue.put(UpdateID.Complete)

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
                
                high_ask_at, high_bid_at = self._calculate_ask_bid(self._tick_data_next.Timestamp,self._tick_data_next.HighPrice)
                low_ask_at, low_bid_at = self._calculate_ask_bid(self._tick_data_next.Timestamp, self._tick_data_next.LowPrice)
                
                self._bar_data_at_last.HighPrice = max(self._bar_data_at_last.HighPrice, self._tick_data_next.HighPrice)
                self._bar_data_at_last.LowPrice = min(self._bar_data_at_last.LowPrice, self._tick_data_next.LowPrice)
                self._bar_data_at_last.ClosePrice = self._tick_data_next.ClosePrice
                self._bar_data_at_last.TickVolume += self._tick_data_next.TickVolume

                try:
                    self._tick_data_next = Bar(*next(self._tick_data_iterator))
                    self._tick_open_next = Tick(self._tick_data_next.Timestamp, *self._calculate_ask_bid(self._tick_data_next.Timestamp, self._tick_data_next.OpenPrice))
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
                    self._update_id_queue.put(UpdateID.AskAboveTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._ask_below_target is not None and self._tick_open_next.Ask <= self._ask_below_target:
                    self._update_id_queue.put(UpdateID.AskBelowTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._bid_above_target is not None and self._tick_open_next.Bid >= self._bid_above_target:
                    self._update_id_queue.put(UpdateID.BidAboveTarget)
                    self._update_args_queue.put(self._tick_open_next)
                    self._update_id_queue.put(UpdateID.Complete)

                if self._bid_below_target is not None and self._tick_open_next.Bid <= self._bid_below_target:
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
            update.Analyst.update_market_offset(self.offset)

        def update_market(update: BarUpdate):
            self._offset -= 1
            update.Analyst.update_market_offset(self._offset)

        def update_results(update: CompleteUpdate):
            self.individual_trades, self.aggregated_trades, self.statistics = update.Manager.Statistics.data(self.account_data, self._start_date, self._stop_date)
            self._log.warning(lambda: str(self.individual_trades))
            self._log.warning(lambda: str(self.aggregated_trades))
            self._log.warning(lambda: str(self.statistics))

        initialisation.on_complete(to=execution, action=init_market, reason="Market Initialized")
        initialisation.on_shutdown(to=termination, action=None, reason="Abruptly Terminated")

        execution.on_bar_closed(to=execution, action=update_market, reason=None)
        execution.on_shutdown(to=termination, action=update_results, reason="Safely Terminated")

        return system_engine

    @timer
    def run(self) -> None:
        self._update_id_queue.put(UpdateID.Account)
        self._update_args_queue.put(self.account_data)

        self._update_id_queue.put(UpdateID.Symbol)
        self._update_args_queue.put(self.symbol_data)

        self._update_id_queue.put(UpdateID.Complete)

        self.deploy(strategy=self.strategy, analyst=self.analyst, manager=self.manager)
