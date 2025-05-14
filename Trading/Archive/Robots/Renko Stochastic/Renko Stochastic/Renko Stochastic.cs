using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Strategies.PositionStrategies;
using AlgorithmicTrading.Strategies.SignalStrategies;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class RenkoStochastic : Robot
    {
        [Parameter("Logging Level", Group = "Logging Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }

        [Parameter("K Period", Group = "Stochastic Oscillator Settings", DefaultValue = 9, MinValue = 1)]
        public int StoKPeriod { get; set; }
        [Parameter("K Slowing", Group = "Stochastic Oscillator Settings", DefaultValue = 3, MinValue = 1)]
        public int StoKSlowing { get; set; }
        [Parameter("D Period", Group = "Stochastic Oscillator Settings", DefaultValue = 9, MinValue = 1)]
        public int StoDPeriod { get; set; }
        [Parameter("MA Type", Group = "Stochastic Oscillator Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType StoMaType { get; set; }
        [Parameter("Overbought Level", Group = "Stochastic Oscillator Settings", DefaultValue = 80.0)]
        public double StoOverboughtLevel { get; set; }
        [Parameter("Oversold Level", Group = "Stochastic Oscillator Settings", DefaultValue = 20.0)]
        public double StoOversoldLevel { get; set; }

        [Parameter("Static Volume (Lots)", Group = "Volume Settings", DefaultValue = 0.1, MinValue = 0.01)]
        public double StaticVolumeLots { get; set; }
        [Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePercentage { get; set; }

        [Parameter("Stop-Loss (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }

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

        [Parameter("Enable", Group = "Telegram Alerts Settings", DefaultValue = false)]
        public bool UseTelegramAlerts { get; set; }
        [Parameter("Token", Group = "Telegram Alerts Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("ChatId", Group = "Telegram Alerts Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        private StochasticOscillator _iSto;
        private Logger _logger;
        private StrategyManager _strategyManager;

        protected override void OnStart()
        {
            _iSto = Indicators.StochasticOscillator(StoKPeriod, StoKSlowing, StoDPeriod, StoMaType);

            var telegram = (UseTelegramAlerts) ? new Telegram(TelegramToken, TelegramChatId) : null;
            _logger = new Logger(LoggerVerboseLevel, this, telegram);

            var position = new PositionManager("MainPosition", null, this, _logger);
            _strategyManager = new StrategyManager(this, _logger);
            var positionStrategy = _strategyManager.CreatePositionStrategyInterface(position);
            var positionStrategySetup = new BasicPositionStrategySetup(UseFirstTakeProfit, FirstTakeProfitPips, FirstTakeProfitVolumePercentage, UseFirstTakeProfitBreakEven, UseSecondTakeProfit, SecondTakeProfitPips, SecondTakeProfitVolumePercentage, UseSecondTakeProfitBreakEven, UseThirdTakeProfit, ThirdTakeProfitPips,
            ThirdTakeProfitVolumePercentage, UseThirdTakeProfitBreakEven);
            positionStrategySetup.SetupStrategy(positionStrategy);

            var signalStrategy = _strategyManager.CreateSignalStrategyInterface(position);
            var signalStrategySetup = new BasicSignalStrategySetup(true, BuyTrigger, SellTrigger, ExitBuyTrigger, ExitSellTrigger, StaticVolumeLots, UseDynamicVolume, DynamicVolumePercentage, StopLossPips, this);
            signalStrategySetup.SetupStrategy(signalStrategy);
        }

        private bool BuyTrigger(PositionManager position)
        {
            return Bars.ClosePrices.Last(3) > Bars.ClosePrices.Last(2) && Bars.ClosePrices.Last(2) < Bars.ClosePrices.Last(1) && _iSto.PercentD.Last(1) < StoOversoldLevel && _iSto.PercentK.Last(1) < StoOversoldLevel && Bars.HighPrices.Last(0) > Bars.HighPrices.Last(1);
        }

        private bool SellTrigger(PositionManager position)
        {
            return Bars.ClosePrices.Last(3) < Bars.ClosePrices.Last(2) && Bars.ClosePrices.Last(2) > Bars.ClosePrices.Last(1) && _iSto.PercentD.Last(1) > StoOverboughtLevel && _iSto.PercentK.Last(1) > StoOverboughtLevel && Bars.HighPrices.Last(0) < Bars.HighPrices.Last(1);
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
