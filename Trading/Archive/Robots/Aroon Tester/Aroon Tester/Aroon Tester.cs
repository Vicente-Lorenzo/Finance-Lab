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
    public class AroonTester : Robot
    {
        [Parameter("Period", Group = "Aroon Settings", DefaultValue = 25, MinValue = 5, MaxValue = 80, Step = 1)]
        public int Period { get; set; }

        [Parameter("Save", Group = "Optimization Settings", DefaultValue = false)]
        public bool SaveOptimization { get; set; }
        [Parameter("Trust Level", Group = "Optimization Settings", DefaultValue = OptimizationManager.OptimizationTrustLevel.Medium)]
        public OptimizationManager.OptimizationTrustLevel TrustLevel { get; set; }

        private const string ManagerId = "MAROON";
        private const string StatisticsId = "MAROON";

        private AverageTrueRange _iAtr;
        private Aroon _iAroon;
        private OptimizationManager _optimization;

        protected override void OnStart()
        {
            _iAtr = Indicators.AverageTrueRange(14, MovingAverageType.Simple);
            _iAroon = Indicators.Aroon(Period);

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
                _optimization.AddIndicatorInformation("Aroon", "Confirmation", new string[] 
                {
                    Period.ToString()
                });
        }

        private bool BuyTrigger(PositionManager position)
        {
            return _iAroon.Up.Last(1) > _iAroon.Down.Last(1) && _iAroon.Up.Last(2) < _iAroon.Down.Last(2);
        }

        private bool SellTrigger(PositionManager position)
        {
            return _iAroon.Up.Last(1) < _iAroon.Down.Last(1) && _iAroon.Up.Last(2) > _iAroon.Down.Last(2);
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
