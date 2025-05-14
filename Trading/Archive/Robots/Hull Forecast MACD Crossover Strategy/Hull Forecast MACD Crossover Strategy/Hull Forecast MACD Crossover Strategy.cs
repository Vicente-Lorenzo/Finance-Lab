using System;
using cAlgo.API;
using AlgorithmicTrading.Alerts;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Schedules;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Strategies.SignalStrategies;
using AlgorithmicTrading.Strategies.BuiltStrategies.PositionStrategies;
using AlgorithmicTrading.Tools;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class HullForecastMACDCrossoverProStrategy : Robot
    {
        [Parameter("Logging Level", Group = "Logging Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }
        
        [Parameter("Source Price", Group = "[Hull Forecast] General Settings")]
        public DataSeries HullSourcePrice { get; set; }
        [Parameter("Coverage Period", Group = "[Hull Forecast] General Settings", DefaultValue = 35)]
        public int HullCoveragePeriod { get; set; }
        [Parameter("Coverage Period Devisor", Group = "[Hull Forecast] General Settings", DefaultValue = 1.7)]
        public double HullPeriodDivisor { get; set; }
        
        [Parameter("Source Price", Group = "[MACD Crossover] General Settings")]
        public DataSeries MacdSourcePrice { get; set; }
        [Parameter("MA Type", Group = "[MACD Crossover] General Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MaType { get; set; }
        [Parameter("Long Cycle", Group = "[MACD Crossover] General Settings", DefaultValue = 26)]
        public int LongCycle { get; set; }
        [Parameter("Short Cycle", Group = "[MACD Crossover] General Settings", DefaultValue = 12)]
        public int ShortCycle { get; set; }
        [Parameter("Signal Periods", Group = "[MACD Crossover] General Settings", DefaultValue = 9)]
        public int Periods { get; set; }
        
        [Parameter("Smoothing MA Period (0 to Disable)", Group = "[MACD Crossover] Reaction Settings", DefaultValue = 0, MinValue = 0)]
        public int SmoothPeriod { get; set; }
        [Parameter("Smoothing MA Type", Group = "[MACD Crossover] Reaction Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SmoothMaType { get; set; }
        [Parameter("Enable Zero Lag", Group = "[MACD Crossover] Reaction Settings", DefaultValue = false)]
        public bool UseZeroLag { get; set; }
        
        [Parameter("Overbought Level", Group = "[MACD Crossover] Level Settings", DefaultValue = 0.0004, Step = 0.00001)]
        public double OverboughtLevel { get; set; }
        [Parameter("Oversold Level", Group = "[MACD Crossover] Level Settings", DefaultValue = -0.0004, Step = 0.00001)]
        public double OversoldLevel { get; set; }

        [Parameter("Static Volume (Lots)", Group = "[First Position] Volume Settings", DefaultValue = 0.1, MinValue = 0.01)]
        public double StaticVolumeLots { get; set; }
        [Parameter("Use Dynamic Volume", Group = "[First Position] Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "[First Position] Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePercentage { get; set; }
        
        [Parameter("Stop-Loss (Pips)", Group = "[First Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }
        [Parameter("Use Trailing-Stop", Group = "[First Position] Stop-Loss Settings", DefaultValue = true)]
        public bool UseTrailingStop { get; set; }
        [Parameter("Trailing-Stop (Pips)", Group = "[First Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopPips { get; set; }
        [Parameter("Trailing-Stop Activation (Pips)", Group = "[First Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopActivationPips { get; set; }
        [Parameter("Update Trailing-Stop On Bar", Group = "[First Position] Stop-Loss Settings", DefaultValue = false)]
        public bool UpdateTrailingStopOnBar { get; set; }

        [Parameter("Enable TP1", Group = "[First Position] First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit { get; set; }
        [Parameter("TP1 (Pips)", Group = "[First Position] First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double FirstTakeProfitPips { get; set; }
        [Parameter("TP1 Partial Close (%)", Group = "[First Position] First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP1 Break-Even", Group = "[First Position] First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven { get; set; }

        [Parameter("Enable TP2", Group = "[First Position] Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit { get; set; }
        [Parameter("TP2 (Pips)", Group = "[First Position] Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double SecondTakeProfitPips { get; set; }
        [Parameter("TP2 Partial Close (%)", Group = "[First Position] Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP2 Break-Even", Group = "[First Position] Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven { get; set; }

        [Parameter("Enable TP3", Group = "[First Position] Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit { get; set; }
        [Parameter("TP3 (Pips)", Group = "[First Position] Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
        public double ThirdTakeProfitPips { get; set; }
        [Parameter("TP3 Partial Close (%)", Group = "[First Position] Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP3 Break-Even", Group = "[First Position] Third Take-Profit Settings", DefaultValue = false)]
        public bool UseThirdTakeProfitBreakEven { get; set; }
        
        [Parameter("Enable Second Position", Group = "[Second Position] General Settings", DefaultValue = true)]
        public bool UseSecondPosition { get; set; }
        
        [Parameter("Static Volume (Lots)", Group = "[Second Position] Volume Settings", DefaultValue = 0.1, MinValue = 0.01)]
        public double StaticVolumeLots2 { get; set; }
        [Parameter("Use Dynamic Volume", Group = "[Second Position] Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume2 { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "[Second Position] Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePercentage2 { get; set; }
        
        [Parameter("Stop-Loss (Pips)", Group = "[Second Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips2 { get; set; }
        [Parameter("Use Trailing-Stop", Group = "[Second Position] Stop-Loss Settings", DefaultValue = true)]
        public bool UseTrailingStop2 { get; set; }
        [Parameter("Trailing-Stop (Pips)", Group = "[Second Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopPips2 { get; set; }
        [Parameter("Trailing-Stop Activation (Pips)", Group = "[Second Position] Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopActivationPips2 { get; set; }
        [Parameter("Update Trailing-Stop On Bar", Group = "[Second Position] Stop-Loss Settings", DefaultValue = false)]
        public bool UpdateTrailingStopOnBar2 { get; set; }

        [Parameter("Enable TP1", Group = "[Second Position] First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit2 { get; set; }
        [Parameter("TP1 (Pips)", Group = "[Second Position] First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double FirstTakeProfitPips2 { get; set; }
        [Parameter("TP1 Partial Close (%)", Group = "[Second Position] First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitVolumePercentage2 { get; set; }
        [Parameter("Enable TP1 Break-Even", Group = "[Second Position] First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven2 { get; set; }

        [Parameter("Enable TP2", Group = "[Second Position] Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit2 { get; set; }
        [Parameter("TP2 (Pips)", Group = "[Second Position] Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double SecondTakeProfitPips2 { get; set; }
        [Parameter("TP2 Partial Close (%)", Group = "[Second Position] Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitVolumePercentage2 { get; set; }
        [Parameter("Enable TP2 Break-Even", Group = "[Second Position] Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven2 { get; set; }

        [Parameter("Enable TP3", Group = "[Second Position] Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit2 { get; set; }
        [Parameter("TP3 (Pips)", Group = "[Second Position] Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
        public double ThirdTakeProfitPips2 { get; set; }
        [Parameter("TP3 Partial Close (%)", Group = "[Second Position] Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitVolumePercentage2 { get; set; }
        [Parameter("Enable TP3 Break-Even", Group = "[Second Position] Third Take-Profit Settings", DefaultValue = false)]
        public bool UseThirdTakeProfitBreakEven2 { get; set; }
        
        [Parameter("Enable", Group = "Trading Time Settings", DefaultValue = false)]
        public bool UseTimeSchedule { get; set; }
        [Parameter("Start Hour", Group = "Trading Time Settings", DefaultValue = 8, MinValue = 0, MaxValue = 23)]
        public int TradingStartHour { get; set; }
        [Parameter("Start Minute", Group = "Trading Time Settings", DefaultValue = 30, MinValue = 0, MaxValue = 59)]
        public int TradingStartMinute { get; set; }
        [Parameter("Stop Hour", Group = "Trading Time Settings", DefaultValue = 21, MinValue = 0, MaxValue = 23)]
        public int TradingStopHour { get; set; }
        [Parameter("Stop Minute", Group = "Trading Time Settings", DefaultValue = 30, MinValue = 0, MaxValue = 59)]
        public int TradingStopMinute { get; set; }
        
        [Parameter("Enable", Group = "Trading Controller Settings", DefaultValue = false)]
        public bool UseControlSchedule { get; set; }
        [Parameter("Max. per Day", Group = "Trading Controller Settings", DefaultValue = 2)]
        public int MaxTradesAtOnce { get; set; }
        [Parameter("Max. per Day", Group = "Trading Controller Settings", DefaultValue = 5)]
        public int MaxTradesPerDay { get; set; }
        
        [Parameter("Enable", Group = "Telegram Alerts Settings", DefaultValue = false)]
        public bool UseTelegramAlerts { get; set; }
        [Parameter("Token", Group = "Telegram Alerts Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("ChatId", Group = "Telegram Alerts Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        private HullForecastMACDCrossoverIndicator _iHullMacd;
        private TickManager _tickManager;
        private Logger _logger;
        private PositionManager _position1, _position2;
        private ScheduleManager _schedule;
        private StrategyManager _strategyManager;
        private double _lastUsedTick;

        protected override void OnStart()
        {
            _iHullMacd = Indicators.GetIndicator<HullForecastMACDCrossoverIndicator>(HullSourcePrice, HullCoveragePeriod, HullPeriodDivisor,
                0.0, MacdSourcePrice, MaType, LongCycle, ShortCycle, Periods, SmoothPeriod, SmoothMaType, UseZeroLag, OverboughtLevel, OversoldLevel,
                false, false, "RoyalBlue", "IndianRed", ChartIconType.Circle, ChartIconType.Circle, 0.0001,
                false, false, "RoyalBlue", "IndianRed", ChartIconType.Circle, ChartIconType.Circle, 0.0001);

            _tickManager = new TickManager(this);
            
            var telegram = (UseTelegramAlerts) ? new TelegramBot(TelegramToken, TelegramChatId, this) : null;
            _logger = new Logger(LoggerVerboseLevel, this, telegram);
            
            _position1 = new PositionManager("Pos1", null, null, this, _logger);
            _position2 = new PositionManager("Pos2", null, null, this, _logger);

            var timeSchedule = UseTimeSchedule ? new TimeSchedule(TradingStartHour, TradingStartMinute, TradingStopHour, TradingStopMinute, this) : null;
            var controlSchedule = UseControlSchedule ? new ControlSchedule(MaxTradesAtOnce, MaxTradesPerDay, null, this) : null;
            _schedule = new ScheduleManager(timeSchedule, controlSchedule);
            
            _strategyManager = new StrategyManager(this, _logger);
            var pos1Strategy = _strategyManager.CreatePositionStrategyInterface("Pos1 Position Strategy", _position1);
            var position1StrategySetup = new AdvancedPositionStrategySetup(UseTrailingStop, TrailingStopPips, TrailingStopActivationPips,
                UpdateTrailingStopOnBar, UseFirstTakeProfit, FirstTakeProfitPips, FirstTakeProfitVolumePercentage, UseFirstTakeProfitBreakEven,
                UseSecondTakeProfit, SecondTakeProfitPips, SecondTakeProfitVolumePercentage, UseSecondTakeProfitBreakEven,
                UseThirdTakeProfit, ThirdTakeProfitPips, ThirdTakeProfitVolumePercentage, UseThirdTakeProfitBreakEven, _tickManager, this);
            position1StrategySetup.SetupStrategy(pos1Strategy);
            
            var pos2Strategy = _strategyManager.CreatePositionStrategyInterface("Pos2 Position Strategy", _position2);
            var position2StrategySetup = new AdvancedPositionStrategySetup(UseTrailingStop2, TrailingStopPips2, TrailingStopActivationPips2,
                UpdateTrailingStopOnBar2, UseFirstTakeProfit2, FirstTakeProfitPips2, FirstTakeProfitVolumePercentage2, UseFirstTakeProfitBreakEven2,
                UseSecondTakeProfit2, SecondTakeProfitPips2, SecondTakeProfitVolumePercentage2, UseSecondTakeProfitBreakEven2,
                UseThirdTakeProfit2, ThirdTakeProfitPips2, ThirdTakeProfitVolumePercentage2, UseThirdTakeProfitBreakEven2, _tickManager, this);
            position2StrategySetup.SetupStrategy(pos2Strategy);

            var signalStrategy = _strategyManager.CreateSignalStrategyInterface("Signal Strategy");
            InitializeSignalStrategy(signalStrategy);
        }

        private void InitializeSignalStrategy(SignalStrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Active Position 1");
            var state2 = strategy.CreateStrategyState("Active Position 1 & 2");
            var state3 = strategy.CreateStrategyState("Active Position 2");

            state0.CreateBarTransition("First Buy Signal", Pos1ScheduledBuyTrigger, Pos1BuyAction, state1);
            state0.CreateBarTransition("First Sell Signal", Pos1ScheduledSellTrigger, Pos1SellAction, state1);

            state1.CreateTickTransition("Position 1 Closed", Pos1ClosedTrigger, null, state0);
            state1.CreateBarTransition("Position 1 Closed", Pos1ClosedTrigger, null, state0);
            state1.CreateBarTransition("Position 1 Exit Signal", Pos1ExitTrigger, Pos1ExitAction, state0);
            state1.CreateBarTransition("Second Buy Signal", Pos2ScheduledBuyTrigger, Pos2BuyAction, state2);
            state1.CreateBarTransition("Second Sell Signal", Pos2ScheduledSellTrigger, Pos2SellAction, state2);
            
            state2.CreateTickTransition("Position 1 Closed", Pos1ClosedTrigger, null, state3);
            state2.CreateBarTransition("Position 1 Closed", Pos1ClosedTrigger, null, state3);
            state2.CreateTickTransition("Position 2 Closed", Pos2ClosedTrigger, null, state1);
            state2.CreateBarTransition("Position 2 Closed", Pos2ClosedTrigger, null, state1);
            state2.CreateBarTransition("Position 1 & 2 Exit Signal", Pos1ExitTrigger, Pos1And2ExitAction, state3);
            
            state3.CreateOrderTransition("Position 2 Closed", Pos2ClosedTrigger, null, state0);
            state3.CreateBarTransition("Position 2 Closed", Pos2ClosedTrigger, null, state0);
            state3.CreateBarTransition("Position 2 Exit Signal", Pos2ExitTrigger, Pos2ExitAction, state0);

            strategy.LoadStrategyState(state0);
        }

        private bool Pos1ClosedTrigger() { return !_position1.IsCurrentlyOpened(); }
        
        private bool Pos2ClosedTrigger() { return !_position2.IsCurrentlyOpened(); }
        
        private bool BuyTrigger()
        {
            return Math.Abs(_lastUsedTick - _tickManager.TickCount) > double.Epsilon && !double.IsNaN(_iHullMacd.HullUpLine.Last(1)) && _iHullMacd.MacdLine.Last(1) < OversoldLevel && 
                   _iHullMacd.SignalLine.Last(1) < _iHullMacd.MacdLine.Last(1) && _iHullMacd.SignalLine.Last(2) > _iHullMacd.MacdLine.Last(2);
        }
        
        private bool SellTrigger()
        {
            return Math.Abs(_lastUsedTick - _tickManager.TickCount) > double.Epsilon && !double.IsNaN(_iHullMacd.HullDownLine.Last(1)) && _iHullMacd.MacdLine.Last(1) > OverboughtLevel && 
                   _iHullMacd.SignalLine.Last(1) > _iHullMacd.MacdLine.Last(1) && _iHullMacd.SignalLine.Last(2) < _iHullMacd.MacdLine.Last(2);
        }

        private bool Pos1ScheduledBuyTrigger() { return _schedule.IsOnSchedule() && BuyTrigger(); }
        
        private bool Pos1ScheduledSellTrigger() { return _schedule.IsOnSchedule() && SellTrigger(); }
        
        private bool Pos2ScheduledBuyTrigger() { return UseSecondPosition && _schedule.IsOnSchedule() && BuyTrigger(); }
        
        private bool Pos2ScheduledSellTrigger() { return UseSecondPosition && _schedule.IsOnSchedule() && SellTrigger(); }

        private bool Pos1BuyAction()
        {
            _lastUsedTick = _tickManager.TickCount;
            return (UseDynamicVolume) ? _position1.OpenPositionDynamic(TradeType.Buy, DynamicVolumePercentage, StopLossPips) : _position1.OpenPositionStatic(TradeType.Buy, Symbol.QuantityToVolumeInUnits(StaticVolumeLots), StopLossPips);
        }

        private bool Pos1SellAction()
        {
            _lastUsedTick = _tickManager.TickCount;
            return (UseDynamicVolume) ? _position1.OpenPositionDynamic(TradeType.Sell, DynamicVolumePercentage, StopLossPips) : _position1.OpenPositionStatic(TradeType.Sell, Symbol.QuantityToVolumeInUnits(StaticVolumeLots), StopLossPips);
        }

        private bool Pos2BuyAction()
        {
            _lastUsedTick = _tickManager.TickCount;
            return (UseDynamicVolume2) ? _position2.OpenPositionDynamic(TradeType.Buy, DynamicVolumePercentage2, StopLossPips2) : _position2.OpenPositionStatic(TradeType.Buy, Symbol.QuantityToVolumeInUnits(StaticVolumeLots2), StopLossPips2);
        }

        private bool Pos2SellAction()
        {
            _lastUsedTick = _tickManager.TickCount;
            return (UseDynamicVolume2) ? _position2.OpenPositionDynamic(TradeType.Sell, DynamicVolumePercentage2, StopLossPips2) : _position2.OpenPositionStatic(TradeType.Sell, Symbol.QuantityToVolumeInUnits(StaticVolumeLots2), StopLossPips2);
        }
        
        private bool Pos1ExitTrigger()
        {
            var ttype = _position1.Position.TradeType;
            return (ttype == TradeType.Buy && SellTrigger()) || (ttype == TradeType.Sell && BuyTrigger());
        }
        
        private bool Pos2ExitTrigger()
        {
            var ttype = _position2.Position.TradeType;
            return (ttype == TradeType.Buy && SellTrigger()) || (ttype == TradeType.Sell && BuyTrigger());
        }

        private bool Pos1ExitAction() { return _position1.ClosePositionTotally(); }
        
        private bool Pos2ExitAction() { return _position2.ClosePositionTotally(); }

        private bool Pos1And2ExitAction() { return Pos1ExitAction() && Pos2ExitAction(); }
    }
}