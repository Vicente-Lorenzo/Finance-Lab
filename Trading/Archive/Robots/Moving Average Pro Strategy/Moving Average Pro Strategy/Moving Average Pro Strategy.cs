using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Schedules;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Strategies.PositionStrategies;
using AlgorithmicTrading.Strategies.SignalStrategies;
using AlgorithmicTrading.Tools;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class MovingAverageProStrategy : Robot
    {
        [Parameter("Logging Level", Group = "Logging Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }

        [Parameter("MA Source", Group = "Moving Average Settings")]
        public DataSeries MaSource { get; set; }
        [Parameter("MA Period", Group = "Moving Average Settings", DefaultValue = 50, MinValue = 1)]
        public int MaPeriod { get; set; }
        [Parameter("MA Type", Group = "Moving Average Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MaType { get; set; }

        [Parameter("Fixed Volume (Lots)", Group = "Volume Settings", DefaultValue = 0.1, MinValue = 0.01)]
        public double FixedVolumeLots { get; set; }
        [Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePercentage { get; set; }

        [Parameter("Stop-Loss (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }
        [Parameter("Use Trailing-Stop", Group = "Stop-Loss Settings", DefaultValue = true)]
        public bool UseTrailingStop { get; set; }
        [Parameter("Trailing-Stop (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopPips { get; set; }
        [Parameter("Trailing-Stop Activation (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double TrailingStopActivationPips { get; set; }
        [Parameter("Update Trailing-Stop On Bar", Group = "Stop-Loss Settings", DefaultValue = false)]
        public bool UpdateTrailingStopOnBar { get; set; }

        [Parameter("Enable TP1", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit { get; set; }
        [Parameter("TP1 (Pips)", Group = "First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double FirstTakeProfitPips { get; set; }
        [Parameter("TP1 Partial Close (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP1 Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven { get; set; }

        [Parameter("Enable TP2", Group = "Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit { get; set; }
        [Parameter("TP2 (Pips)", Group = "Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double SecondTakeProfitPips { get; set; }
        [Parameter("TP2 Partial Close (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP2 Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven { get; set; }

        [Parameter("Enable TP3", Group = "Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit { get; set; }
        [Parameter("TP3 (Pips)", Group = "Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
        public double ThirdTakeProfitPips { get; set; }
        [Parameter("TP3 Partial Close (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitVolumePercentage { get; set; }
        [Parameter("Enable TP3 Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
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

        private MovingAverage _iMA;
        private Logger _logger;
        private ScheduleManager _schedule;
        private StrategyManager _strategyManager;
        private TradeType _lastTrendDirection;

        protected override void OnStart()
        {
            _iMA = Indicators.MovingAverage(MaSource, MaPeriod, MaType);
            _lastTrendDirection = Bars.ClosePrices.Last(1) > _iMA.Result.Last(1) ? TradeType.Buy : TradeType.Sell;
            _logger = new Logger(LoggerVerboseLevel, this, (UseTelegramAlerts) ? new Telegram(TelegramToken, TelegramChatId) : null);
            var position = new PositionManager("Position", null, null, this, _logger);
            var timeSchedule = (UseTimeSchedule) ? new TimeSchedule(TradingStartHour, TradingStartMinute, TradingStopHour, TradingStopMinute, this) : null;
            var controlSchedule = (UseControlSchedule) ? new ControlSchedule(MaxTradesAtOnce, MaxTradesPerDay, (UseOthersFilter) ? position.ManagerGroupLabel : null, this) : null;
            _schedule = new ScheduleManager(timeSchedule, controlSchedule);

            _strategyManager = new StrategyManager(this, _logger);
            var positionStrategy = _strategyManager.CreatePositionStrategyInterface(position);
            var positionStrategySetup = new AdvancedPositionStrategySetup(UseTrailingStop, TrailingStopPips, TrailingStopActivationPips, UpdateTrailingStopOnBar, UseFirstTakeProfit, FirstTakeProfitPips, FirstTakeProfitVolumePercentage, UseFirstTakeProfitBreakEven, UseSecondTakeProfit, SecondTakeProfitPips,
            SecondTakeProfitVolumePercentage, UseSecondTakeProfitBreakEven, UseThirdTakeProfit, ThirdTakeProfitPips, ThirdTakeProfitVolumePercentage, UseThirdTakeProfitBreakEven, new TickManager(this), this);
            positionStrategySetup.SetupStrategy(positionStrategy);

            var signalStrategy = _strategyManager.CreateSignalStrategyInterface(position);
            var signalStrategySetup = new BasicSignalStrategySetup(true, BuyTrigger, SellTrigger, ExitBuyTrigger, ExitSellTrigger, FixedVolumeLots, UseDynamicVolume, DynamicVolumePercentage, StopLossPips, this);
            signalStrategySetup.SetupStrategy(signalStrategy);
        }

        private bool BuyTrigger(PositionManager position)
        {
            if (!(_schedule.IsOnSchedule() && _lastTrendDirection == TradeType.Sell && Bars.ClosePrices.Last(1) > _iMA.Result.Last(1)))
                return false;
            _lastTrendDirection = TradeType.Buy;
            return true;
        }

        private bool SellTrigger(PositionManager position)
        {
            if (!(_schedule.IsOnSchedule() && _lastTrendDirection == TradeType.Buy && Bars.ClosePrices.Last(1) < _iMA.Result.Last(1)))
                return false;
            _lastTrendDirection = TradeType.Sell;
            return true;
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
