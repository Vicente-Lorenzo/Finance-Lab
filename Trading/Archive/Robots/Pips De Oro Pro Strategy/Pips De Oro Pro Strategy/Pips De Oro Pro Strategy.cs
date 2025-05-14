using AlgorithmicTrading.Alerts;
using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Strategies;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class PipsDeOroProStrategy : Robot
    {
        [Parameter("Verbose Level", Group = "Logger Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }

        [Parameter("Source", Group = "Signal Moving Average Settings")]
        public DataSeries SignalMaSource { get; set; }
        [Parameter("Period", Group = "Signal Moving Average Settings", DefaultValue = 6)]
        public int SignalMaPeriod { get; set; }
        [Parameter("Type", Group = "Signal Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SignalMaType { get; set; }

        [Parameter("Source", Group = "Baseline Moving Average Settings")]
        public DataSeries BaselineMaSource { get; set; }
        [Parameter("Period", Group = "Baseline Moving Average Settings", DefaultValue = 30)]
        public int BaselineMaPeriod { get; set; }
        [Parameter("Type", Group = "Baseline Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType BaselineMaType { get; set; }

        [Parameter("Static Volume (Units)", Group = "Volume Settings", DefaultValue = 1000, MinValue = 0.1)]
        public double StaticVolumeUnits { get; set; }
        [Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePerc { get; set; }

        [Parameter("Stop-Loss Multiplier", Group = "Stop-Loss Settings", DefaultValue = 1.0, MinValue = 0.1)]
        public double StopLossMultiplier { get; set; }

        [Parameter("Enable", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit { get; set; }
        [Parameter("Take-Profit Multiplier", Group = "First Take-Profit Settings", DefaultValue = 1.0, MinValue = 0.1)]
        public double FirstTakeProfitMultiplier { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit { get; set; }
        [Parameter("Take-Profit Multiplier", Group = "Second Take-Profit Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double SecondTakeProfitMultiplier { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit { get; set; }
        [Parameter("Take-Profit Multiplier", Group = "Third Take-Profit Settings", DefaultValue = 3.0, MinValue = 0.1)]
        public double ThirdTakeProfitMultiplier { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
        public bool UseThirdTakeProfitBreakEven { get; set; }

        [Parameter("Telegram Alerts", Group = "Alert Settings", DefaultValue = false)]
        public bool UseTelegramAlerts { get; set; }
        [Parameter("Telegram Token", Group = "Alert Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("Telegram ChatId", Group = "Alert Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        private MovingAverage _iSignalMa, _iBaselineMa;
        private Logger _logger;
        private PositionManager _position;
        private StrategyInterface _riskManagment, _signalManagment;
        private StrategyManager _strategyManager;
        private TelegramBot _telegram;
        private double _lastEntryRangePips;

        protected override void OnStart()
        {
            _iSignalMa = Indicators.MovingAverage(SignalMaSource, SignalMaPeriod, SignalMaType);
            _iBaselineMa = Indicators.MovingAverage(BaselineMaSource, BaselineMaPeriod, BaselineMaType);

            _telegram = new TelegramBot(TelegramToken, TelegramChatId, this);
            _logger = new Logger(LoggerVerboseLevel, this, (UseTelegramAlerts) ? _telegram : null);
            _position = new PositionManager("T", "T", "T", Symbol, this, _logger);

            _riskManagment = new StrategyInterface("Risk Managment", this, _logger);
            _signalManagment = new StrategyInterface("Signal Managment", this, _logger);

            InitializeRiskManagment();
            InitializeSignalManagment();

            _strategyManager = new StrategyManager(_riskManagment, _signalManagment, this);
        }

        private void InitializeRiskManagment()
        {
            var state0 = _riskManagment.CreateStrategyState("No Position");
            var state1 = _riskManagment.CreateStrategyState("Checking TP1");
            var state2 = _riskManagment.CreateStrategyState("Checking TP2");
            var state3 = _riskManagment.CreateStrategyState("Checking TP3");
            var state4 = _riskManagment.CreateStrategyState("Waiting Close");

            state0.CreateBarTransition("Position Opened", PositionOpenedTrigger, null, state1);

            state1.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateTickTransition("Scaling-Out Position", FirstScalingOutTrigger, FirstScalingOutAction, state2);

            state2.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state2.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state2.CreateTickTransition("Scaling-Out Position", SecondScalingOutTrigger, SecondScalingOutAction, state3);

            state3.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state3.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state3.CreateTickTransition("Scaling-Out Position", ThirdScalingOutTrigger, ThirdScalingOutAction, state4);

            state4.CreateTickTransition("Hit Stop-Loss", PositionClosedTrigger, null, state0);
            state4.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            _riskManagment.LoadStrategyState(state0);
        }

        private bool PositionOpenedTrigger()
        {
            return _position.IsCurrentlyOpened();
        }

        private bool PositionClosedTrigger()
        {
            return !_position.IsCurrentlyOpened();
        }

        private bool FirstScalingOutTrigger()
        {
            return UseFirstTakeProfit && _position.Position.Pips >= FirstTakeProfitMultiplier * _lastEntryRangePips;
        }

        private bool FirstScalingOutAction()
        {
            return !_position.ClosePositionPartially(FirstTakeProfitParcialCloseVolumePerc) || (!UseFirstTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private bool SecondScalingOutTrigger()
        {
            return UseSecondTakeProfit && _position.Position.Pips >= SecondTakeProfitMultiplier * _lastEntryRangePips;
        }

        private bool SecondScalingOutAction()
        {
            return !_position.ClosePositionPartially(SecondTakeProfitParcialCloseVolumePerc) || (!UseSecondTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private bool ThirdScalingOutTrigger()
        {
            return UseThirdTakeProfit && _position.Position.Pips >= ThirdTakeProfitMultiplier * _lastEntryRangePips;
        }

        private bool ThirdScalingOutAction()
        {
            return !_position.ClosePositionPartially(ThirdTakeProfitParcialCloseVolumePerc) || (!UseThirdTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private void InitializeSignalManagment()
        {
            var state0 = _signalManagment.CreateStrategyState("No Position");
            var state1 = _signalManagment.CreateStrategyState("Normal Position");

            state0.CreateBarTransition("Normal Buy Signal", NormalBuyTrigger, BuyAction, state1);
            state0.CreateBarTransition("Normal Sell Signal", NormalSellTrigger, SellAction, state1);

            state1.CreateOrderTransition("Hit Stop-Limit", HitStopLimitTrigger, null, state0);
            state1.CreateBarTransition("Hit Stop-Limit", HitStopLimitTrigger, null, state0);
            state1.CreateBarTransition("Normal Exit Signal", NormalExitTrigger, ExitAction, state0);

            _signalManagment.LoadStrategyState(state0);
        }

        private bool NormalBuyTrigger()
        {
            return _iSignalMa.Result.Last(1) > _iBaselineMa.Result.Last(1) && _iSignalMa.Result.Last(2) < _iBaselineMa.Result.Last(2);
        }

        private bool NormalSellTrigger()
        {
            return _iSignalMa.Result.Last(1) < _iBaselineMa.Result.Last(1) && _iSignalMa.Result.Last(2) > _iBaselineMa.Result.Last(2);
        }

        private bool NormalExitTrigger()
        {
            var ttype = _position.Position.TradeType;
            return (ttype == TradeType.Buy && NormalSellTrigger()) || (ttype == TradeType.Sell && NormalBuyTrigger());
        }

        private bool HitStopLimitTrigger()
        {
            return !_position.IsCurrentlyOpened();
        }

        private bool BuyAction()
        {
            _lastEntryRangePips = _position.ConvertDeltaPriceToPips(Bars.HighPrices.Last(1) - Bars.LowPrices.Last(1));
            return (UseDynamicVolume) ? _position.OpenPositionPro(TradeType.Buy, DynamicVolumePerc, StopLossMultiplier * _lastEntryRangePips) : _position.OpenPosition(TradeType.Buy, StaticVolumeUnits, StopLossMultiplier * _lastEntryRangePips);
        }

        private bool SellAction()
        {
            _lastEntryRangePips = _position.ConvertDeltaPriceToPips(Bars.HighPrices.Last(1) - Bars.LowPrices.Last(1));
            return (UseDynamicVolume) ? _position.OpenPositionPro(TradeType.Sell, DynamicVolumePerc, StopLossMultiplier * _lastEntryRangePips) : _position.OpenPosition(TradeType.Sell, StaticVolumeUnits, StopLossMultiplier * _lastEntryRangePips);
        }

        private bool ExitAction()
        {
            return _position.ClosePositionTotally();
        }
    }
}
