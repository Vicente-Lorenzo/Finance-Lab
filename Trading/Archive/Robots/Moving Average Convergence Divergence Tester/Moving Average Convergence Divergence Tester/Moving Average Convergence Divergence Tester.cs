using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Strategies.PositionStrategies;
using AlgorithmicTrading.Strategies.SignalStrategies;
using AlgorithmicTrading.Tools;
using AlgorithmicTrading.Statistics;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class MovingAverageConvergenceDivergenceTester : Robot
    {
        [Parameter("Long Period", Group = "Moving Averages Settings", DefaultValue = 26, MinValue = 1, MaxValue = 100, Step = 2)]
        public int LongPeriod { get; set; }
        [Parameter("Short Period", Group = "Moving Averages Settings", DefaultValue = 12, MinValue = 1, MaxValue = 100, Step = 2)]
        public int ShortPeriod { get; set; }
        [Parameter("Signal Period", Group = "Moving Averages Settings", DefaultValue = 9, MinValue = 1, MaxValue = 100, Step = 2)]
        public int SignalPeriod { get; set; }

        [Parameter("Save", Group = "Optimization Settings", DefaultValue = false)]
        public bool SaveOptimization { get; set; }
        [Parameter("Trust Level", Group = "Optimization Settings", DefaultValue = OptimizationManager.OptimizationTrustLevel.Medium)]
        public OptimizationManager.OptimizationTrustLevel TrustLevel { get; set; }

        private const string ManagerId = "MMACD";
        private const string StatisticsId = "SMACD";

        private AverageTrueRange _iAtr;
        private MacdCrossOver _iMACD;
        private OptimizationManager _optimization;

        protected override void OnStart()
        {
            if (ShortPeriod >= LongPeriod)
                Stop();
            _iAtr = Indicators.AverageTrueRange(14, MovingAverageType.Simple);
            _iMACD = Indicators.MacdCrossOver(LongPeriod, ShortPeriod, SignalPeriod);

            var logger = new Logger(Logger.VerboseLevel.Warn, this);
            var position = new PositionManager(ManagerId, StatisticsId, this, logger);
            var manager = new StrategyManager(this, logger);

            var riskManagment = manager.CreatePositionStrategyInterface(position);
            var riskManagmentSetup = new NnfxPositionStrategySetup(1.5, 1.5, false, 1.0, 50, _iAtr, new TickManager(this), this);
            riskManagmentSetup.SetupStrategy(riskManagment);

            var signalManagment = manager.CreateSignalStrategyInterface(position);
            var signalManagmentSetup = new NnfxSignalStrategySetup(BuyTrigger, SellTrigger, ExitBuyTrigger, ExitSellTrigger, 2, 1.5, _iAtr, this);
            signalManagmentSetup.SetupStrategy(signalManagment);

            _optimization = new OptimizationManager(SaveOptimization ? new StatisticsManager(StatisticsId, this) : null, this);
            if (SaveOptimization)
                _optimization.AddIndicatorInformation("Moving Average Convergence Divergence", "Confirmation", new string[] 
                {
                    LongPeriod.ToString(),
                    ShortPeriod.ToString(),
                    SignalPeriod.ToString(),
                });
        }

        private bool BuyTrigger(PositionManager position)
        {
            return _iMACD.MACD.Last(1) > _iMACD.Signal.Last(1) && _iMACD.MACD.Last(2) < _iMACD.Signal.Last(2);
        }

        private bool SellTrigger(PositionManager position)
        {
            return _iMACD.MACD.Last(1) < _iMACD.Signal.Last(1) && _iMACD.MACD.Last(2) > _iMACD.Signal.Last(2);
        }

        private bool ExitBuyTrigger(PositionManager position)
        {
            return position.Position.TradeType == TradeType.Buy && SellTrigger(position);
        }

        private bool ExitSellTrigger(PositionManager position)
        {
            return position.Position.TradeType == TradeType.Sell && BuyTrigger(position);
        }

        protected override double GetFitness(GetFitnessArgs args)
        {
            var fitness = _optimization.CalculateFitnessValue(args);
            if (SaveOptimization)
                _optimization.SaveOptimization(args, TrustLevel);
            return fitness;
        }
    }
}
