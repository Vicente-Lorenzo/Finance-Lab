import struct
import win32file

from typing import Type
from datetime import datetime

from Library.Classes import *
from Library.Database import DatabaseAPI
from Library.Parameters import Parameters
from Library.Utils import timer, timestamp_to_datetime

from Library.Robots.Protocol import *
from Library.Robots.Engine import MachineAPI
from Library.Robots.Analyst import AnalystAPI
from Library.Robots.Manager import ManagerAPI
from Library.Robots.Strategy import StrategyAPI
from Library.Robots.System import SystemAPI

class RealtimeSystemAPI(SystemAPI):

    SENTINEL = -1.0
    
    def __init__(self,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 strategy: Type[StrategyAPI],
                 parameters: Parameters,
                 iid: str):
        
        super().__init__(broker=broker, group=group, symbol=symbol, timeframe=timeframe, strategy=strategy, parameters=parameters)
        
        self._iid: str = iid
        self._pipe = None

        self._sync_buffer: list[Bar] = []
        self._initial_account: Account | None = None
        self._start_timestamp: datetime | None = None
        self._stop_timestamp: datetime | None = None

    def __enter__(self):
        self.strategy = self._strategy(money_management=self.parameters.MoneyManagement, risk_management=self.parameters.RiskManagement, signal_management=self.parameters.SignalManagement)
        self.analyst = AnalystAPI(analyst_management=self.parameters.AnalystManagement)
        self.manager = ManagerAPI(manager_management=self.parameters.ManagerManagement)
        
        self._bar_db: DatabaseAPI = DatabaseAPI(broker=self._broker, group=self._group, symbol=self._symbol, timeframe=self._timeframe)
        self._bar_db.__enter__()
        try:
            self._pipe = win32file.CreateFile(f"\\\\.\\pipe\\{self._broker}\\{self._symbol}\\{self._timeframe}\\{self._iid}",
                                              win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None,
                                              win32file.OPEN_EXISTING, 0, None)
        except Exception as e:
            self._log.error(lambda: str(e))
            raise e
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._bar_db:
            self._bar_db.__exit__(None, None, None)
        if self._pipe:
            win32file.CloseHandle(self._pipe)
        return super().__exit__(exc_type, exc_value, exc_traceback)

    def _send_action(self, fmt: str, action_id: ActionID, *args) -> None:
        content = struct.pack(fmt, action_id.value, *args)
        win32file.WriteFile(self._pipe, content)

    def send_action_complete(self, action: CompleteAction) -> None:
        self._send_action("<1b", action.ActionID)

    def send_action_open(self, action: OpenBuyAction | OpenSellAction) -> None:
        sl_pips = action.StopLoss if action.StopLoss is not None else self.SENTINEL
        tp_pips = action.TakeProfit if action.TakeProfit is not None else self.SENTINEL
        self._send_action("<1b1b3d", action.ActionID, action.PositionType.value, action.Volume, sl_pips, tp_pips)

    def send_action_modify_volume(self, action: ModifyBuyVolumeAction | ModifySellVolumeAction) -> None:
        self._send_action("<1b1i1d", action.ActionID, action.PositionID, action.Volume)

    def send_action_modify_stop_loss(self, action: ModifyBuyStopLossAction | ModifySellStopLossAction) -> None:
        sl_price = action.StopLoss if action.StopLoss is not None else self.SENTINEL
        self._send_action("<1b1i1d", action.ActionID, action.PositionID, sl_price)

    def send_action_modify_take_profit(self, action: ModifyBuyTakeProfitAction | ModifySellTakeProfitAction) -> None:
        tp_price = action.TakeProfit if action.TakeProfit is not None else self.SENTINEL
        self._send_action("<1b1i1d", action.ActionID, action.PositionID, tp_price)
        
    def send_action_close(self, action: CloseBuyAction | CloseSellAction) -> None:
        self._send_action("<1b1i", action.ActionID, action.PositionID)

    def send_action_ask_above_target(self, action: AskAboveTargetAction) -> None:
        target = action.Ask if action.Ask is not None else self.SENTINEL
        self._send_action("<1b1d", action.ActionID, target)

    def send_action_ask_below_target(self, action: AskBelowTargetAction) -> None:
        target = action.Ask if action.Ask is not None else self.SENTINEL
        self._send_action("<1b1d", action.ActionID, target)

    def send_action_bid_above_target(self, action: BidAboveTargetAction) -> None:
        target = action.Bid if action.Bid is not None else self.SENTINEL
        self._send_action("<1b1d", action.ActionID, target)

    def send_action_bid_below_target(self, action: BidBelowTargetAction) -> None:
        target = action.Bid if action.Bid is not None else self.SENTINEL
        self._send_action("<1b1d", action.ActionID, target)

    def _receive_update(self, size: str) -> tuple:
        buffer = win32file.AllocateReadBuffer(struct.calcsize(size))
        _, content = win32file.ReadFile(self._pipe, buffer)
        return struct.unpack(size, content)

    def receive_update_id(self) -> UpdateID:
        return UpdateID(*self._receive_update("<1b"))

    def receive_update_account(self) -> Account:
        content = self._receive_update(size="<2b8d1b")
        account_type = content[0]
        asset_type = content[1]
        balance = content[2]
        equity = content[3]
        credit = content[4]
        leverage = content[5]
        margin_used = content[6]
        margin_free = content[7]
        margin_level = content[8]
        margin_level = margin_level if margin_level is not self.SENTINEL else None
        margin_stop_level = content[9]
        margin_mode = content[10]
        return Account(
            AccountType=account_type,
            AssetType=asset_type,
            Balance=balance,
            Equity=equity,
            Credit=credit,
            Leverage=leverage,
            MarginUsed=margin_used,
            MarginFree=margin_free,
            MarginLevel=margin_level,
            MarginStopLevel=margin_stop_level,
            MarginMode=margin_mode
        )

    def receive_update_symbol(self) -> Symbol:
        content = self._receive_update(size="<2b1i2d1q4d1b2d2b")
        base_asset = content[0]
        quote_asset = content[1]
        digits = content[2]
        point_size = content[3]
        pip_size = content[4]
        lot_size = content[5]
        volume_min = content[6]
        volume_max = content[7]
        volume_step = content[8]
        commission = content[9]
        commission_mode = content[10]
        swap_long = content[11]
        swap_short = content[12]
        swap_mode = content[13]
        swap_extra_day = content[14]
        return Symbol(
            BaseAssetType=base_asset,
            QuoteAssetType=quote_asset,
            Digits=digits,
            PointSize=point_size,
            PipSize=pip_size,
            LotSize=lot_size,
            VolumeInUnitsMin=volume_min,
            VolumeInUnitsMax=volume_max,
            VolumeInUnitsStep=volume_step,
            Commission=commission,
            CommissionMode=commission_mode,
            SwapLong=swap_long,
            SwapShort=swap_short,
            SwapMode=swap_mode,
            SwapExtraDay=swap_extra_day
        )

    def receive_update_position(self) -> Position:
        content = self._receive_update(size="<1i2b1q12d")
        position_id = content[0]
        position_type = PositionType(content[1])
        trade_type = TradeType(content[2])
        timestamp = timestamp_to_datetime(content[3], milliseconds=True)
        entry_price = content[4]
        volume = content[5]
        quantity = content[6]
        points = content[7]
        pips = content[8]
        gross_pnl = content[9]
        commission_pnl = content[10]
        swap_pnl = content[11]
        net_pnl = content[12]
        sl = content[13]
        tp = content[14]
        sl = sl if sl is not self.SENTINEL else None
        tp = tp if tp is not self.SENTINEL else None
        used_margin = content[15]
        return Position(
            PositionID=position_id,
            PositionType=position_type,
            TradeType=trade_type,
            EntryTimestamp=timestamp,
            EntryPrice=entry_price,
            Volume=volume,
            Quantity=quantity,
            Points=points,
            Pips=pips,
            GrossPnL=gross_pnl,
            CommissionPnL=commission_pnl,
            SwapPnL=swap_pnl,
            NetPnL=net_pnl,
            StopLoss=sl,
            TakeProfit=tp,
            UsedMargin=used_margin
        )

    def receive_update_trade(self) -> Trade:
        content = self._receive_update(size="<2i2b2q10d")
        position_id = content[0]
        trade_id = content[1]
        position_type = PositionType(content[2])
        trade_type = TradeType(content[3])
        entry_timestamp = timestamp_to_datetime(content[4], milliseconds=True)
        exit_timestamp = timestamp_to_datetime(content[5], milliseconds=True)
        entry_price = content[6]
        exit_price = content[7]
        volume = content[8]
        quantity = content[9]
        points = content[10]
        pips = content[11]
        gross_pnl = content[12]
        commission_pnl = content[13]
        swap_pnl = content[14]
        net_pnl = content[15]
        return Trade(
            PositionID=position_id,
            TradeID=trade_id,
            PositionType=position_type,
            TradeType=trade_type,
            EntryTimestamp=entry_timestamp,
            ExitTimestamp=exit_timestamp,
            EntryPrice=entry_price,
            ExitPrice=exit_price,
            Volume=volume,
            Quantity=quantity,
            Points=points,
            Pips=pips,
            GrossPnL=gross_pnl,
            CommissionPnL=commission_pnl,
            SwapPnL=swap_pnl,
            NetPnL=net_pnl
        )

    def receive_update_bar(self) -> Bar:
        content = self._receive_update(size="<1q4d1q")
        timestamp = timestamp_to_datetime(content[0], milliseconds=True)
        open_price = content[1]
        high_price = content[2]
        low_price = content[3]
        close_price = content[4]
        volume = content[5]
        return Bar(
            Timestamp=timestamp,
            OpenPrice=open_price,
            HighPrice=high_price,
            LowPrice=low_price,
            ClosePrice=close_price,
            TickVolume=volume
        )

    def receive_update_target(self) -> Tick:
        content = self._receive_update(size="<1q2d")
        timestamp = timestamp_to_datetime(content[0], milliseconds=True)
        ask = content[1]
        bid = content[2]
        return Tick(
            Timestamp=timestamp,
            Ask=ask,
            Bid=bid
        )

    def system_management(self) -> MachineAPI:

        system_engine = MachineAPI("System Management")

        initialisation = system_engine.create_state(name="Initialisation", end=False)
        execution = system_engine.create_state(name="Execution", end=False)
        termination = system_engine.create_state(name="Termination", end=True)
            
        def sync_market(update: BarUpdate):
            self._sync_buffer.append(update.Bar)
    
        def init_market(update: CompleteUpdate):
            self._initial_account = update.Manager.Account.data()
            self._start_timestamp = self._sync_buffer[-1].Timestamp
            update.Analyst.init_market_data(self._sync_buffer)

        def update_market(update: BarUpdate):
            self._stop_timestamp = update.Bar.Timestamp
            update.Analyst.update_market_data(update.Bar)
    
        def update_database(update: CompleteUpdate):
            self._bar_db.push_symbol_data(update.Manager.Symbol.data())
            self._bar_db.push_market_data(update.Analyst.Market.data())
            self.individual_trades, self.aggregated_trades, self.statistics = update.Manager.Statistics.data(self._initial_account, self._start_timestamp, self._stop_timestamp)
            self._log.warning(lambda: str(self.individual_trades))
            self._log.warning(lambda: str(self.aggregated_trades))
            self._log.warning(lambda: str(self.statistics))

        initialisation.on_bar_closed(to=initialisation, action=sync_market, reason=None)
        initialisation.on_complete(to=execution, action=init_market, reason="Market Initialized")
        initialisation.on_shutdown(to=termination, action=None, reason="Abruptly Terminated")

        execution.on_bar_closed(to=execution, action=update_market, reason=None)
        execution.on_shutdown(to=termination, action=update_database, reason="Safely Terminated")

        return system_engine

    @timer
    def run(self) -> None:
        self.deploy(strategy=self.strategy, analyst=self.analyst, manager=self.manager)
