using System.Diagnostics;
using cAlgo.API;
using cAlgo.Indicators;
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
    public class ConfirmationTesterBHE : Robot
    {
        private Stopwatch sw;

        private Logger Logger { get; set; }
        private PositionManager PositionManager { get; set; }
        private StatisticsManager StatisticsManager { get; set; }
        private AverageTrueRange iATR { get; set; }
        private NnfxRiskManagment RiskManagment { get; set; }
        private NnfxNormalStrategy SignalStrategy { get; set; }
        private StrategyManager StrategyManager { get; set; }

        private void InitializeLoggers()
        {
            Logger = new Logger(Logger.VerboseLevel.Debug, this);
        }

        private void InitializePositionManager()
        {
            PositionManager = new PositionManager("T", "T", "T", Symbol, this, logger: Logger);
        }

        private void InitializeStatisticsManager()
        {
            StatisticsManager = new StatisticsManager("T", this, Logger);
        }

        private void InitializeRiskManagment()
        {
            RiskManagment = new NnfxRiskManagment(iATR, PositionManager, this, Logger);
        }

        private void InitializeSignalStrategy()
        {
            SignalStrategy = new NnfxNormalStrategy(iATR, PositionManager, this, Logger, NormalBuyTrigger, NormalSellTrigger, NormalExitTrigger, riskPerTrade: 2);
        }

        private void InitializeStrategyManager()
        {
            StrategyManager = new StrategyManager(RiskManagment.Strategy, SignalStrategy.Strategy, this);
        }

        protected override void OnStart()
        {
            InitializeLoggers();
            InitializePositionManager();
            InitializeStatisticsManager();
            InitializeIndicators();
            InitializeRiskManagment();
            InitializeSignalStrategy();
            InitializeStrategyManager();
            sw = new Stopwatch();
            sw.Start();
        }

        protected override void OnStop()
        {
            sw.Stop();
            StatisticsManager.LogStatistics();
            Print("Elapsed " + sw.Elapsed);
        }

        // ==========================================================
        // Adicionar parametros do indicador a ser testado
        [Parameter("1st MA Period", DefaultValue = 2, MinValue = 1)]
        public int FisrtMAPeriod { get; set; }
        [Parameter("2nd MA Period", DefaultValue = 10, MinValue = 1)]
        public int SecondMAPeriod { get; set; }
        [Parameter("3rd MA Period", DefaultValue = 5, MinValue = 1)]
        public int ThirdMAPeriod { get; set; }
        [Parameter("Trigger MA period", DefaultValue = 3, MinValue = 1)]
        public int TriggerMAPeriod { get; set; }
        [Parameter("MA Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }

        // Modificar a variavel global do indicator a ser testado
        private CustomBHErgodic iBHE { get; set; }

        // Modificar o inicializador do indicador a ser testado
        private void InitializeIndicators()
        {
            iATR = Indicators.AverageTrueRange(14, MovingAverageType.Exponential);
            iBHE = Indicators.GetIndicator<CustomBHErgodic>(Bars.ClosePrices, FisrtMAPeriod, SecondMAPeriod, ThirdMAPeriod, TriggerMAPeriod, MAType);
        }

        // Modificar as funcoes de entrada e saida em mercado
        private bool NormalBuyTrigger()
        {
            return iBHE.UpLine.Last(1) > iBHE.DownLine.Last(1) && iBHE.DownLine.Last(2) > iBHE.UpLine.Last(2);
        }

        private bool NormalSellTrigger()
        {
            return iBHE.DownLine.Last(1) > iBHE.UpLine.Last(1) && iBHE.UpLine.Last(2) > iBHE.DownLine.Last(2);
        }

        private bool NormalExitTrigger()
        {
            TradeType ttype = PositionManager.Position.TradeType;
            return (ttype == TradeType.Buy && iBHE.DownLine.Last(1) > iBHE.UpLine.Last(1) && iBHE.UpLine.Last(2) > iBHE.DownLine.Last(2)) || (ttype == TradeType.Sell && iBHE.UpLine.Last(1) > iBHE.DownLine.Last(1) && iBHE.DownLine.Last(2) > iBHE.UpLine.Last(2));
        }
        // ==========================================================
    }
}
