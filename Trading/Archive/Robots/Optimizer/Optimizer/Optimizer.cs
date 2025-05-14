using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Statistics;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Strategies.RiskManagment;
using AlgorithmicTrading.Strategies.SignalManagment;

namespace cAlgo
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class Optimizer : Robot
    {
        [Parameter("Aroon Period", DefaultValue = 25, MinValue = 1)]
        public int AroonPeriod { get; set; }

        private Logger _logger;
        private PositionManager _positionManager;
        private StatisticsManager _statisticsManager;
        private AverageTrueRange _iAtr;
        private Aroon _iAroon;
        private NnfxRiskManagment _riskManagment;
        private NnfxNormalStrategy _signalStrategy;
        private StrategyManager _strategyManager;

        protected override void OnStart()
        {
            _logger = new Logger(Logger.VerboseLevel.Stats, this);
            _positionManager = new PositionManager("T", "T", "T", Symbol, this, logger: _logger);
            _statisticsManager = new StatisticsManager("T", this, _logger);
            _iAtr = Indicators.AverageTrueRange(14, MovingAverageType.Exponential);
            _iAroon = Indicators.Aroon(AroonPeriod);
            _riskManagment = new NnfxRiskManagment(_iAtr, _positionManager, this, _logger);
            _signalStrategy = new NnfxNormalStrategy(_iAtr, _positionManager, this, _logger, NormalBuyTrigger, NormalSellTrigger, NormalExitTrigger);
            _strategyManager = new StrategyManager(_riskManagment.Strategy, _signalStrategy.Strategy, this);
        }

        protected override void OnStop()
        {
            _statisticsManager.LogStatistics();
        }

        private bool NormalBuyTrigger()
        {
            return _iAroon.Up.Last(1) > _iAroon.Down.Last(1) && _iAroon.Down.Last(2) > _iAroon.Up.Last(2);
        }

        private bool NormalSellTrigger()
        {
            return _iAroon.Down.Last(1) > _iAroon.Up.Last(1) && _iAroon.Up.Last(2) > _iAroon.Down.Last(2);
        }

        private bool NormalExitTrigger()
        {
            var ttype = _positionManager.Position.TradeType;
            return (ttype == TradeType.Buy && _iAroon.Down.Last(1) > _iAroon.Up.Last(1) && _iAroon.Up.Last(2) > _iAroon.Down.Last(2)) || (ttype == TradeType.Sell && _iAroon.Up.Last(1) > _iAroon.Down.Last(1) && _iAroon.Down.Last(2) > _iAroon.Up.Last(2));
        }
    }
}
