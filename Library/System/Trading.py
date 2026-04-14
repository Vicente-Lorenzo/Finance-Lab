import queue
from typing import Type, Callable

from Library.Dataframe import pl
from Library.Database import DatabaseAPI
from Library.Parameters import Parameters
from Library.Utils import timer

from Library.Protocol import *
from Library.Engine import MachineAPI
from Library.Analyst import AnalystAPI
from Library.Manager import ManagerAPI
from Library.Strategy import StrategyAPI
from Library.System import SystemAPI

from Library.Dataclass.Account import AccountAPI, AccountType, AssetType, MarginMode
from Library.Dataclass.Symbol import SymbolAPI, SpreadType, CommissionType, CommissionMode, SwapType, SwapMode, DayOfWeek
from Library.Dataclass.Position import PositionAPI, PositionType, TradeType
from Library.Dataclass.Trade import TradeAPI
from Library.Dataclass.Bar import BarAPI
from Library.Dataclass.Tick import TickAPI, TickMode

class TradingSystemAPI(SystemAPI):

    SENTINEL = -1.0

    def __init__(self,
                 api,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 strategy: Type[StrategyAPI],
                 parameters: Parameters) -> None:

        super().__init__(
            broker=broker,
            group=group,
            symbol=symbol,
            timeframe=timeframe,
            strategy=strategy,
            parameters=parameters
        )

        self.api = api
        self.queue = queue.Queue()
        self._current_update = None
        self._current_update_id = None

        self._sync_buffer: list[BarAPI] = []
        self._initial_account: AccountAPI | None = None
        self._start_timestamp = None
        self._stop_timestamp = None

        self._ask_base_conversion = lambda: 1.0
        self._bid_base_conversion = lambda: 1.0
        self._ask_quote_conversion = lambda: 1.0
        self._bid_quote_conversion = lambda: 1.0

        self._last_bar: BarAPI | None = None

    def __enter__(self):
        self.strategy = self._strategy(
            money_management=self.parameters.MoneyManagement,
            risk_management=self.parameters.RiskManagement,
            signal_management=self.parameters.SignalManagement
        )
        self.analyst = AnalystAPI(analyst_management=self.parameters.AnalystManagement)
        self.manager = ManagerAPI(manager_management=self.parameters.ManagerManagement)

        self._bar_db: DatabaseAPI = DatabaseAPI(
            broker=self._broker,
            group=self._group,
            symbol=self._symbol,
            timeframe=self._timeframe
        )
        self._bar_db.__enter__()

        self._setup_conversions()
        
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._bar_db:
            self._bar_db.__exit__(None, None, None)
        return super().__exit__(exc_type, exc_value, exc_traceback)

    def _setup_conversions(self):
        base_asset = self.api.Symbol.BaseAsset
        quote_asset = self.api.Symbol.QuoteAsset
        account_asset = self.api.Account.Asset

        self._ask_base_conversion, self._bid_base_conversion = self._find_conversions(base_asset, account_asset)
        self._ask_quote_conversion, self._bid_quote_conversion = self._find_conversions(quote_asset, account_asset)

    def _find_conversions(self, from_asset, to_asset) -> tuple[Callable[[], float], Callable[[], float]]:
        if from_asset == to_asset:
            return (lambda: 1.0, lambda: 1.0)
        
        for symbol_name in self.api.Symbols:
            try:
                symbol = self.api.Symbols.GetSymbol(symbol_name)
                if symbol.BaseAsset == from_asset and symbol.QuoteAsset == to_asset:
                    return (lambda s=symbol: s.Ask, lambda s=symbol: s.Bid)
                if symbol.QuoteAsset == from_asset and symbol.BaseAsset == to_asset:
                    return (lambda s=symbol: 1.0 / s.Bid, lambda s=symbol: 1.0 / s.Ask)
            except:
                continue
        
        self._log.warning(lambda: f"No conversion symbol found for {from_asset} -> {to_asset}")
        return (lambda: 1.0, lambda: 1.0)

    def _get_tick(self) -> TickAPI:
        return TickAPI(
            Timestamp=self.api.Server.Time,
            Ask=self.api.Symbol.Ask,
            Bid=self.api.Symbol.Bid,
            AskBaseConversion=self._ask_base_conversion(),
            BidBaseConversion=self._bid_base_conversion(),
            AskQuoteConversion=self._ask_quote_conversion(),
            BidQuoteConversion=self._bid_quote_conversion(),
            symbol=self.manager.Symbol
        )

    def _convert_account(self, acc) -> AccountAPI:
        return AccountAPI(
            AccountType=AccountType(acc.AccountType),
            AssetType=AssetType[acc.Asset.Name],
            Balance=acc.Balance,
            Equity=acc.Equity,
            Credit=acc.Credit,
            Leverage=acc.PreciseLeverage,
            MarginUsed=acc.Margin,
            MarginFree=acc.FreeMargin,
            MarginLevel=acc.MarginLevel if acc.MarginLevel is not None else None,
            MarginStopLevel=acc.StopOutLevel,
            MarginMode=MarginMode(acc.TotalMarginCalculationType)
        )

    def _convert_symbol(self, sym) -> SymbolAPI:
        return SymbolAPI(
            BaseAssetType=AssetType[sym.BaseAsset.Name],
            QuoteAssetType=AssetType[sym.QuoteAsset.Name],
            Digits=sym.Digits,
            PointSize=sym.TickSize,
            PipSize=sym.PipSize,
            LotSize=sym.LotSize,
            VolumeMin=sym.VolumeInUnitsMin,
            VolumeMax=sym.VolumeInUnitsMax,
            VolumeStep=sym.VolumeInUnitsStep,
            Commission=sym.Commission,
            CommissionMode=CommissionMode(sym.CommissionType),
            SwapLong=sym.SwapLong,
            SwapShort=sym.SwapShort,
            SwapMode=SwapMode(sym.SwapCalculationType),
            SwapExtraDay=DayOfWeek((sym.Swap3DaysRollover - 1) % 7 if sym.Swap3DaysRollover is not None else 2) # Wednesday default
        )

    def _convert_position(self, pos) -> PositionAPI:
        try:
            pos_type = PositionType[pos.Comment]
        except:
            pos_type = PositionType.Normal

        return PositionAPI(
            PositionID=pos.Id,
            PositionType=pos_type,
            TradeType=TradeType(pos.TradeType),
            Volume=pos.VolumeInUnits,
            Quantity=pos.Quantity,
            EntryTimestamp=pos.EntryTime,
            EntryPrice=pos.EntryPrice,
            StopLossPrice=pos.StopLoss if pos.StopLoss is not None else None,
            TakeProfitPrice=pos.TakeProfit if pos.TakeProfit is not None else None,
            ExitPrice=pos.CurrentPrice,
            GrossPnL=pos.GrossProfit,
            CommissionPnL=pos.Commissions,
            SwapPnL=pos.Swap,
            NetPnL=pos.NetProfit,
            UsedMargin=pos.Margin,
            symbol=self.manager.Symbol,
            entry_balance=self.manager.Account.Balance if self.manager.Account else 0.0
        )

    def _convert_trade(self, trd) -> TradeAPI:
        try:
            pos_type = PositionType[trd.Comment]
        except:
            pos_type = PositionType.Normal

        return TradeAPI(
            PositionID=trd.PositionId,
            TradeID=trd.ClosingDealId,
            PositionType=pos_type,
            TradeType=TradeType(trd.TradeType),
            Volume=trd.VolumeInUnits,
            Quantity=trd.Quantity,
            EntryTimestamp=trd.EntryTime,
            ExitTimestamp=trd.ClosingTime,
            EntryPrice=trd.EntryPrice,
            ExitPrice=trd.ClosingPrice,
            GrossPnL=trd.GrossProfit,
            CommissionPnL=trd.Commissions,
            SwapPnL=trd.Swap,
            NetPnL=trd.NetProfit,
            symbol=self.manager.Symbol,
            entry_balance=self.manager.Account.Balance if self.manager.Account else 0.0
        )

    def _convert_bar(self, b) -> BarAPI:
        tick = self._get_tick()
        return BarAPI(
            Timestamp=b.OpenTime,
            gap_timestamp=tick.Timestamp.DateTime,
            gap_ask=tick.Ask.Price,
            gap_bid=tick.Bid.Price,
            gap_ask_base_conversion=tick.AskBaseConversion,
            gap_bid_base_conversion=tick.BidBaseConversion,
            gap_ask_quote_conversion=tick.AskQuoteConversion,
            gap_bid_quote_conversion=tick.BidQuoteConversion,
            open_timestamp=b.OpenTime,
            open_ask=b.Open,
            open_bid=b.Open,
            open_ask_base_conversion=tick.AskBaseConversion,
            open_bid_base_conversion=tick.BidBaseConversion,
            open_ask_quote_conversion=tick.AskQuoteConversion,
            open_bid_quote_conversion=tick.BidQuoteConversion,
            high_timestamp=b.OpenTime,
            high_ask=b.High,
            high_bid=b.High,
            high_ask_base_conversion=tick.AskBaseConversion,
            high_bid_base_conversion=tick.BidBaseConversion,
            high_ask_quote_conversion=tick.AskQuoteConversion,
            high_bid_quote_conversion=tick.BidQuoteConversion,
            low_timestamp=b.OpenTime,
            low_ask=b.Low,
            low_bid=b.Low,
            low_ask_base_conversion=tick.AskBaseConversion,
            low_bid_base_conversion=tick.BidBaseConversion,
            low_ask_quote_conversion=tick.AskQuoteConversion,
            low_bid_quote_conversion=tick.BidQuoteConversion,
            close_timestamp=b.OpenTime,
            close_ask=b.Close,
            close_bid=b.Close,
            close_ask_base_conversion=tick.AskBaseConversion,
            close_bid_base_conversion=tick.BidBaseConversion,
            close_ask_quote_conversion=tick.AskQuoteConversion,
            close_bid_quote_conversion=tick.BidQuoteConversion,
            TickVolume=b.TickVolume,
            symbol=self.manager.Symbol
        )

    def receive_update_id(self) -> UpdateID:
        self._current_update_id, self._current_update = self.queue.get()
        return self._current_update_id

    def receive_update_account(self) -> AccountAPI:
        return self._current_update

    def receive_update_symbol(self) -> SymbolAPI:
        return self._current_update

    def receive_update_position(self) -> PositionAPI:
        return self._current_update

    def receive_update_trade(self) -> TradeAPI:
        return self._current_update

    def receive_update_bar(self) -> BarAPI:
        return self._current_update

    def receive_update_target(self) -> TickAPI:
        return self._current_update

    def send_action_complete(self, action: CompleteAction) -> None:
        pass

    def send_action_open(self, action: OpenBuyAction | OpenSellAction) -> None:
        trade_type = 0 if isinstance(action, OpenBuyAction) else 1
        self.api.ExecuteMarketOrder(
            trade_type,
            self.api.Symbol.Name,
            action.Volume,
            self.api.InstanceId,
            action.StopLoss,
            action.TakeProfit,
            action.PositionType.name
        )

    def send_action_modify_volume(self, action: ModifyBuyVolumeAction | ModifySellVolumeAction) -> None:
        for pos in self.api.Positions:
            if pos.Id == action.PositionID:
                pos.ModifyVolume(action.Volume)
                break

    def send_action_modify_stop_loss(self, action: ModifyBuyStopLossAction | ModifySellStopLossAction) -> None:
        for pos in self.api.Positions:
            if pos.Id == action.PositionID:
                pos.ModifyStopLossPrice(action.StopLoss)
                break

    def send_action_modify_take_profit(self, action: ModifyBuyTakeProfitAction | ModifySellTakeProfitAction) -> None:
        for pos in self.api.Positions:
            if pos.Id == action.PositionID:
                pos.ModifyTakeProfitPrice(action.TakeProfit)
                break

    def send_action_close(self, action: CloseBuyAction | CloseSellAction) -> None:
        for pos in self.api.Positions:
            if pos.Id == action.PositionID:
                self.api.ClosePosition(pos)
                break

    def send_action_ask_above_target(self, action: AskAboveTargetAction) -> None:
        self._ask_above_target = action.Ask

    def send_action_ask_below_target(self, action: AskBelowTargetAction) -> None:
        self._ask_below_target = action.Ask

    def send_action_bid_above_target(self, action: BidAboveTargetAction) -> None:
        self._bid_above_target = action.Bid

    def send_action_bid_below_target(self, action: BidBelowTargetAction) -> None:
        self._bid_below_target = action.Bid

    def system_management(self) -> MachineAPI:
        system_engine = MachineAPI("System Management")
        initialisation = system_engine.create_state(name="Initialisation", end=False)
        execution = system_engine.create_state(name="Execution", end=False)
        termination = system_engine.create_state(name="Termination", end=True)
            
        def sync_market(update: BarUpdate):
            self._sync_buffer.append(update.Bar)
    
        def init_market(update: CompleteUpdate):
            self._initial_account = update.Manager.Account
            self._start_timestamp = self._sync_buffer[-1].Timestamp.DateTime
            update.Analyst.init_market_data(self._sync_buffer)

        def update_market(update: BarUpdate):
            self._stop_timestamp = update.Bar.Timestamp.DateTime
            update.Analyst.update_market_data(update.Bar)
    
        def update_database(update: CompleteUpdate):
            self._bar_db.push_symbol_data(update.Manager.Symbol)
            self._bar_db.push_market_data(update.Analyst.Market.data())
            self.individual_trades, self.aggregated_trades, self.statistics = update.Manager.Statistics.data(self._initial_account, self._start_timestamp, self._stop_timestamp)

        initialisation.on_bar_closed(to=initialisation, action=sync_market, reason=None)
        initialisation.on_complete(to=execution, action=init_market, reason="Market Initialized")
        initialisation.on_shutdown(to=termination, action=None, reason="Abruptly Terminated")

        execution.on_bar_closed(to=execution, action=update_market, reason=None)
        execution.on_shutdown(to=termination, action=update_database, reason="Safely Terminated")

        return system_engine

    def on_tick(self):
        tick = self._get_tick()
        if hasattr(self, "_ask_above_target") and self._ask_above_target and tick.Ask.Price >= self._ask_above_target:
            self.queue.put((UpdateID.AskAboveTarget, tick))
        elif hasattr(self, "_ask_below_target") and self._ask_below_target and tick.Ask.Price <= self._ask_below_target:
            self.queue.put((UpdateID.AskBelowTarget, tick))
        elif hasattr(self, "_bid_above_target") and self._bid_above_target and tick.Bid.Price >= self._bid_above_target:
            self.queue.put((UpdateID.BidAboveTarget, tick))
        elif hasattr(self, "_bid_below_target") and self._bid_below_target and tick.Bid.Price <= self._bid_below_target:
            self.queue.put((UpdateID.BidBelowTarget, tick))
        else:
            self.queue.put((UpdateID.TickClosed, tick))
        self.queue.put((UpdateID.Complete, None))

    def on_bar_closed(self):
        bar = self._convert_bar(self.api.Bars.Last(1))
        self.queue.put((UpdateID.BarClosed, bar))
        self.queue.put((UpdateID.Complete, None))

    def on_position_opened(self, pos):
        update_id = UpdateID.OpenedBuy if pos.TradeType == 0 else UpdateID.OpenedSell
        self.queue.put((update_id, self._convert_position(pos)))
        self.queue.put((UpdateID.Complete, None))

    def on_shutdown(self):
        self.queue.put((UpdateID.Shutdown, None))

    @timer
    def run(self) -> None:
        self.queue.put((UpdateID.Account, self._convert_account(self.api.Account)))
        self.queue.put((UpdateID.Symbol, self._convert_symbol(self.api.Symbol)))
        self.queue.put((UpdateID.Complete, None))
        self.deploy(strategy=self.strategy, analyst=self.analyst, manager=self.manager)
