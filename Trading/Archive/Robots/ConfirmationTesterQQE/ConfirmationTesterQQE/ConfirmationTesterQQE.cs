using cAlgo.API;
using cAlgo.Indicators;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Logger;
using AlgorithmicTrading.Position;
using AlgorithmicTrading.Strategy.RiskManagment;
using AlgorithmicTrading.Strategy.SignalManagment;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class ConfirmationTesterQQE : Robot
    {
        // ==========================================================
        // Adicionar parametros do indicador a ser testado
        [Parameter("RSI Period", DefaultValue = 8, MinValue = 1)]
        public int RsiPeriod { get; set; }
        [Parameter("RSI Smoothing Period", DefaultValue = 1, MinValue = 1)]
        public int RsiSmoothingPeriod { get; set; }
        [Parameter("ATR Period", DefaultValue = 14, MinValue = 1)]
        public int AtrPeriod { get; set; }
        [Parameter("Fast ATR Multipliers", DefaultValue = 3.0, MinValue = 0.1)]
        public double FastAtrMult { get; set; }
        [Parameter("MA Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }
        // ==========================================================

        private LoggerManager Logger { get; set; }
        private PositionManager PosManager { get; set; }
        private AverageTrueRange iATR { get; set; }
        private NNFXRiskManagment RiskManagment { get; set; }
        private NNFXNormalStrategy SignalStrategy { get; set; }

        // ==========================================================
        // Modificar a variavel global do indicator a ser testado
        private CustomQualitativeQuantitativeEstimation iQQE { get; set; }
        private string TesterName = "QQETester";
        // ==========================================================

        private void InitializeLoggers()
        {
            Logger = new LoggerManager();
            Logger.AddLogger(new RobotLogger(LoggerConstants.VerboseLevel.Info, this));
        }

        private void InitializePositionManager()
        {
            PosManager = new PositionManager(TesterName, Symbol, this, logger: Logger);
        }

        // ==========================================================
        // Modificar o inicializador do indicador a ser testado
        private void InitializeIndicators()
        {
            iATR = Indicators.AverageTrueRange(14, MovingAverageType.Exponential);
            iQQE = Indicators.GetIndicator<CustomQualitativeQuantitativeEstimation>(Bars.ClosePrices, RsiPeriod, RsiSmoothingPeriod, AtrPeriod, FastAtrMult, MAType);
        }
        // ==========================================================

        private void InitializeRiskManagment()
        {
            RiskManagment = new NNFXRiskManagment(Symbol.Name, iATR, PosManager, this, Logger);
        }

        private void InitializeSignalStrategy()
        {
            SignalStrategy = new NNFXNormalStrategy(Symbol.Name, iATR, PosManager, this, Logger, NormalBuyTrigger, NormalSellTrigger, NormalExitTrigger, riskPerTrade: 2);
        }

        // ==========================================================
        // Modificar as funcoes de entrada e saida em mercado
        private bool NormalBuyTrigger(bool barUpdate)
        {
            return barUpdate && PosManager.HasNoActivePosition() && iQQE.UpLine.Last(1) > iQQE.DownLine.Last(1) && iQQE.DownLine.Last(2) > iQQE.UpLine.Last(2);
        }

        private bool NormalSellTrigger(bool barUpdate)
        {
            return barUpdate && PosManager.HasNoActivePosition() && iQQE.DownLine.Last(1) > iQQE.UpLine.Last(1) && iQQE.UpLine.Last(2) > iQQE.DownLine.Last(2);
        }

        private bool NormalExitTrigger(bool barUpdate)
        {
            if (!barUpdate)
                return false;
            if (PosManager.HasNoActivePosition())
                return false;
            TradeType ttype = (TradeType)PosManager.PositionTradeType;
            return (ttype == TradeType.Buy && iQQE.DownLine.Last(1) > iQQE.UpLine.Last(1) && iQQE.UpLine.Last(2) > iQQE.DownLine.Last(2)) || (ttype == TradeType.Sell && iQQE.UpLine.Last(1) > iQQE.DownLine.Last(1) && iQQE.DownLine.Last(2) > iQQE.UpLine.Last(2));
        }
        // ==========================================================

        private void UpdateRobotStrategy(bool barUpdate)
        {
            if (RiskManagment.UpdateRiskManagmentStrategy(barUpdate) || SignalStrategy.UpdateSignalManagmentStrategy(barUpdate))
                UpdateRobotStrategy(barUpdate);
        }

        // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Main Execution %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        protected override void OnStart()
        {
            InitializeLoggers();
            InitializePositionManager();
            InitializeIndicators();
            InitializeRiskManagment();
            InitializeSignalStrategy();
        }

        protected override void OnTick()
        {
            UpdateRobotStrategy(barUpdate: false);
        }

        protected override void OnBar()
        {
            UpdateRobotStrategy(barUpdate: true);
        }

        protected override void OnStop()
        {
            if (PosManager.HasActivePosition())
                PosManager.ClosePositionTotally();
            UpdateRobotStrategy(false);
        }
    }
}
