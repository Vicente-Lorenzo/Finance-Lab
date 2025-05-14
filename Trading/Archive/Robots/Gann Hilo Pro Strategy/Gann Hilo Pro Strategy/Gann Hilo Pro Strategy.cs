using System;
using cAlgo.API;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Strategies;
using cAlgo.Indicators;
using AlgorithmicTrading.Schedules;
using AlgorithmicTrading.Strategies.SignalStrategies;
using AlgorithmicTrading.Tools;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class GannHiloProStrategy : Robot
    {
        [Parameter("Verbose Level", Group = "Logger Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }

        [Parameter("Period", Group = "Gann Hilo Settings", DefaultValue = 13, MinValue = 1)]
        public int GannHiloPeriod { get; set; }
        [Parameter("MA Type", Group = "Gann Hilo Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType GannHiloMaType { get; set; }

        [Parameter("Fixed Volume (Lots)", Group = "Volume Settings", DefaultValue = 0.1, MinValue = 0.1)]
        public double FixedVolumeLots { get; set; }
        [Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePerc { get; set; }

        [Parameter("Stop-Loss (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }
        [Parameter("Enable Trailing-Stop", Group = "Stop-Loss Settings", DefaultValue = true)]
        public bool UseTrailingStop { get; set; }

        [Parameter("Enable", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double FirstTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double SecondTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
        public double ThirdTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
        public bool UseThirdTakeProfitBreakEven { get; set; }

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

        [Parameter("Enable", Group = "Daily Trading Controller Settings", DefaultValue = false)]
        public bool UseControlSchedule { get; set; }
        [Parameter("Max. At Once", Group = "Daily Trading Controller Settings", DefaultValue = 5)]
        public int MaxTradesAtOnce { get; set; }
        [Parameter("Max. per Day", Group = "Daily Trading Controller Settings", DefaultValue = 5)]
        public int MaxTradesPerDay { get; set; }
        [Parameter("Filter Other's Trades", Group = "Daily Trading Controller Settings", DefaultValue = true)]
        public bool UseOthersFilter { get; set; }

        [Parameter("Telegram Alerts", Group = "Alert Settings", DefaultValue = false)]
        public bool UseTelegramAlerts { get; set; }
        [Parameter("Telegram Token", Group = "Alert Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("Telegram ChatId", Group = "Alert Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        private GannHiLoProIndicator _iGannHilo;
        private ScheduleManager _schedule;
        private StrategyManager _strategyManager;
        private int _lastTrailingStopUpdateCount = -1;

        protected override void OnStart()
        {
            _iGannHilo = Indicators.GetIndicator<GannHiLoProIndicator>(GannHiloPeriod, GannHiloMaType, false);

            var logger = new Logger(LoggerVerboseLevel, this, (UseTelegramAlerts) ? new Telegram(TelegramToken, TelegramChatId) : null);
            var position = new PositionManager("Position", null, this, logger);
            var timeSchedule = (UseTimeSchedule) ? new TimeSchedule(TradingStartHour, TradingStartMinute, TradingStopHour, TradingStopMinute, this) : null;
            var controlSchedule = (UseControlSchedule) ? new ControlSchedule(MaxTradesAtOnce, MaxTradesPerDay, (UseOthersFilter) ? position.ManagerGroupLabel : null, this) : null;
            _schedule = new ScheduleManager(timeSchedule, controlSchedule);

            _strategyManager = new StrategyManager(this, logger);
            var positionStrategy = _strategyManager.CreatePositionStrategyInterface(position);
            InitializeRiskManagment(positionStrategy);

            var signalStrategy = _strategyManager.CreateSignalStrategyInterface(position);
            var signalStrategySetup = new BasicSignalStrategySetup(true, BuyTrigger, SellTrigger, ExitBuyTrigger, ExitSellTrigger, FixedVolumeLots, UseDynamicVolume, DynamicVolumePerc, StopLossPips, this);
            signalStrategySetup.SetupStrategy(signalStrategy);
        }

        private void InitializeRiskManagment(StrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Checking TP1");
            var state2 = strategy.CreateStrategyState("Checking TP2");
            var state3 = strategy.CreateStrategyState("Checking TP3");
            var state4 = strategy.CreateStrategyState("Waiting Close");

            state0.CreateBarTransition("Position Opened", PositionOpenedTrigger, null, state1);

            state1.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateTickTransition("Scaling-Out Position", FirstScalingOutTrigger, FirstScalingOutAction, state2);
            state1.CreateBarTransition("Updating Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state1);

            state2.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state2.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state2.CreateTickTransition("Scaling-Out Position", SecondScalingOutTrigger, SecondScalingOutAction, state3);
            state2.CreateBarTransition("Updating Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state2);

            state3.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state3.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state3.CreateTickTransition("Scaling-Out Position", ThirdScalingOutTrigger, ThirdScalingOutAction, state4);
            state3.CreateBarTransition("Updating Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state3);

            state4.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state4.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            strategy.LoadStrategyState(state0);
        }

        private bool PositionOpenedTrigger(PositionManager position)
        {
            return position.IsCurrentlyOpened();
        }

        private bool PositionClosedTrigger(PositionManager position)
        {
            return !position.IsCurrentlyOpened();
        }

        private bool FirstScalingOutTrigger(PositionManager position)
        {
            return UseFirstTakeProfit && position.Position.Pips >= FirstTakeProfitPips;
        }

        private bool FirstScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(FirstTakeProfitParcialCloseVolumePerc) || (!UseFirstTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool SecondScalingOutTrigger(PositionManager position)
        {
            return UseSecondTakeProfit && position.Position.Pips >= SecondTakeProfitPips;
        }

        private bool SecondScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(SecondTakeProfitParcialCloseVolumePerc) || (!UseSecondTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool ThirdScalingOutTrigger(PositionManager position)
        {
            return UseThirdTakeProfit && position.Position.Pips >= ThirdTakeProfitPips;
        }

        private bool ThirdScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(ThirdTakeProfitParcialCloseVolumePerc) || (!UseThirdTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool UpdateTrailingStopTrigger(PositionManager position)
        {
            return UseTrailingStop && _lastTrailingStopUpdateCount != Bars.Count;
        }

        private bool UpdateTrailingStopAction(PositionManager position)
        {
            _lastTrailingStopUpdateCount = Bars.Count;
            return (position.Position.TradeType == TradeType.Buy) ? position.ModifyEntryStopLoss(MathLibrary.ConvertDeltaPriceToPips(Math.Abs(position.Position.EntryPrice - _iGannHilo.UpSeries.Last(1)), Symbol.PipSize)) : position.ModifyEntryStopLoss(MathLibrary.ConvertDeltaPriceToPips(Math.Abs(position.Position.EntryPrice - _iGannHilo.DownSeries.Last(1)), Symbol.PipSize));
        }

        private bool BuyTrigger(PositionManager position)
        {
            return _schedule.IsOnSchedule() && Bars.ClosePrices.Last(1) > _iGannHilo.MainSeries.Last(1) && Bars.ClosePrices.Last(2) < _iGannHilo.MainSeries.Last(2);
        }

        private bool SellTrigger(PositionManager position)
        {
            return _schedule.IsOnSchedule() && Bars.ClosePrices.Last(1) < _iGannHilo.MainSeries.Last(1) && Bars.ClosePrices.Last(2) > _iGannHilo.MainSeries.Last(2);
        }

        private bool ExitBuyTrigger(PositionManager position)
        {
            return position.Position.TradeType == TradeType.Buy && SellTrigger(position);
        }

        private bool ExitSellTrigger(PositionManager position)
        {
            return position.Position.TradeType == TradeType.Sell && BuyTrigger(position);
        }
    }
}
