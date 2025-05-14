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
    public class SuperTrendTester : Robot
    {
        [Parameter("Period", Group = "SuperTrend Settings", DefaultValue = 10, MinValue = 4, MaxValue = 40, Step = 2)]
        public int Period { get; set; }
        [Parameter("Multiplier", Group = "SuperTrend Settings", DefaultValue = 3.0, MinValue = 1.0, MaxValue = 6.0, Step = 0.2)]
        public double Multiplier { get; set; }

        [Parameter("Save", Group = "Optimization Settings", DefaultValue = false)]
        public bool SaveOptimization { get; set; }
        [Parameter("Trust Level", Group = "Optimization Settings", DefaultValue = OptimizationManager.OptimizationTrustLevel.Medium)]
        public OptimizationManager.OptimizationTrustLevel TrustLevel { get; set; }

        private const string ManagerId = "MSTrend";
        private const string StatisticsId = "SSTrend";

        private AverageTrueRange _iAtr;
        private Supertrend _iSTrend;
        private OptimizationManager _optimization;

        protected override void OnStart()
        {
            _iAtr = Indicators.AverageTrueRange(14, MovingAverageType.Simple);
            _iSTrend = Indicators.Supertrend(Period, Multiplier);

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
                _optimization.AddIndicatorInformation("SuperTrend", "Confirmation", new string[] 
                {
                    Period.ToString(),
                    Multiplier.ToString()
                });
        }

        private bool BuyTrigger(PositionManager position)
        {
            return _iSTrend.UpTrend.Last(1) < Bars.ClosePrices.Last(1) && _iSTrend.DownTrend.Last(2) > Bars.ClosePrices.Last(2);
        }

        private bool SellTrigger(PositionManager position)
        {
            return _iSTrend.DownTrend.Last(1) > Bars.ClosePrices.Last(1) && _iSTrend.UpTrend.Last(2) < Bars.ClosePrices.Last(2);
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
