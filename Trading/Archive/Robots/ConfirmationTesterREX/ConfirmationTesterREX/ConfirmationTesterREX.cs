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
    public class ConfirmationTesterREX : Robot
    {
        // ==========================================================
        // Adicionar parametros do indicador a ser testado
        [Parameter("Period", DefaultValue = 14)]
        public int SignalPeriod { get; set; }
        [Parameter("Smoothing Period", DefaultValue = 14)]
        public int SmoothingPeriod { get; set; }
        [Parameter("MA Type", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MAType { get; set; }
        // ==========================================================

        private LoggerManager Logger { get; set; }
        private PositionManager PosManager { get; set; }
        private AverageTrueRange iATR { get; set; }
        private NNFXRiskManagment RiskManagment { get; set; }
        private NNFXNormalStrategy SignalStrategy { get; set; }

        // ==========================================================
        // Modificar a variavel global do indicator a ser testado
        private CustomRexOscillator iREX { get; set; }
        private string TesterName = "REXTester";
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
            iREX = Indicators.GetIndicator<CustomRexOscillator>(Bars.OpenPrices, Bars.HighPrices, Bars.LowPrices, Bars.ClosePrices, SignalPeriod, SmoothingPeriod, MAType);
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
            return barUpdate && PosManager.HasNoActivePosition() && iREX.UpLine.Last(1) > iREX.DownLine.Last(1) && iREX.DownLine.Last(2) > iREX.UpLine.Last(2);
        }

        private bool NormalSellTrigger(bool barUpdate)
        {
            return barUpdate && PosManager.HasNoActivePosition() && iREX.DownLine.Last(1) > iREX.UpLine.Last(1) && iREX.UpLine.Last(2) > iREX.DownLine.Last(2);
        }

        private bool NormalExitTrigger(bool barUpdate)
        {
            if (!barUpdate)
                return false;
            if (PosManager.HasNoActivePosition())
                return false;
            TradeType ttype = (TradeType)PosManager.PositionTradeType;
            return (ttype == TradeType.Buy && iREX.DownLine.Last(1) > iREX.UpLine.Last(1) && iREX.UpLine.Last(2) > iREX.DownLine.Last(2)) || (ttype == TradeType.Sell && iREX.UpLine.Last(1) > iREX.DownLine.Last(1) && iREX.DownLine.Last(2) > iREX.UpLine.Last(2));
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
