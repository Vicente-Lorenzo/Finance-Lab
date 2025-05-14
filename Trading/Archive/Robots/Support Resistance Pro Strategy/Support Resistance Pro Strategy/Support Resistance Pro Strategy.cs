using System;
using cAlgo.API;
using AlgorithmicTrading.Alerts;
using AlgorithmicTrading.Loggers;
using AlgorithmicTrading.Positions;
using AlgorithmicTrading.Strategies;
using AlgorithmicTrading.Schedules;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class SupportResistanceProStrategy : Robot
    {
        [Parameter("Verbose Level", Group = "Logger Settings", DefaultValue = Logger.VerboseLevel.Info)]
        public Logger.VerboseLevel LoggerVerboseLevel { get; set; }

        [Parameter("Resistance Tolerance (Pips)", Group = "Support Resistance Settings", DefaultValue = 5.0, MinValue = 0.1)]
        public double ResistanceTolerancePips { get; set; }
        [Parameter("Support Tolerance (Pips)", Group = "Support Resistance Settings", DefaultValue = 5.0, MinValue = 0.1)]
        public double SupportTolerancePips { get; set; }
        [Parameter("Enable Limit Orders", Group = "Support Resistance Settings", DefaultValue = false)]
        public bool UseLimitOrders { get; set; }
        [Parameter("Resistance Limit Target (Pips)", Group = "Support Resistance Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double ResistanceLimitTargetPips { get; set; }
        [Parameter("Support Limit Target (Pips)", Group = "Support Resistance Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double SupportLimitTargetPips { get; set; }

        [Parameter("Static Volume (Units)", Group = "Volume Settings", DefaultValue = 1000, MinValue = 0.1)]
        public double StaticVolumeUnits { get; set; }
        [Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
        public bool UseDynamicVolume { get; set; }
        [Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
        public double DynamicVolumePerc { get; set; }

        [Parameter("Stop-Loss (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }

        [Parameter("Enable", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double FirstTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
        public double FirstTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
        public bool UseFirstTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Second Take-Profit Settings", DefaultValue = true)]
        public bool UseSecondTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double SecondTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
        public double SecondTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
        public bool UseSecondTakeProfitBreakEven { get; set; }

        [Parameter("Enable", Group = "Third Take-Profit Settings", DefaultValue = true)]
        public bool UseThirdTakeProfit { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
        public double ThirdTakeProfitPips { get; set; }
        [Parameter("Partial Close Volume (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
        public double ThirdTakeProfitParcialCloseVolumePerc { get; set; }
        [Parameter("Enable Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
        public bool UseThirdTakeProfitBreakEven { get; set; }
        
        [Parameter("Enable", Group = "Trading Time Settings", DefaultValue = false)]
        public bool UseScheduleTrading { get; set; }
        [Parameter("Start Hour", Group = "Trading Time Settings", DefaultValue = 8, MinValue = 0, MaxValue = 23)]
        public int TradingStartHour { get; set; }
        [Parameter("Start Minute", Group = "Trading Time Settings", DefaultValue = 30, MinValue = 0, MaxValue = 59)]
        public int TradingStartMinute { get; set; }
        [Parameter("Stop Hour", Group = "Trading Time Settings", DefaultValue = 21, MinValue = 0, MaxValue = 23)]
        public int TradingStopHour { get; set; }
        [Parameter("Stop Minute", Group = "Trading Time Settings", DefaultValue = 30, MinValue = 0, MaxValue = 59)]
        public int TradingStopMinute { get; set; }
        
        [Parameter("Enable", Group = "Daily Trading Controller Settings", DefaultValue = false)]
        public bool UseDailyTradingController { get; set; }
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

        private SupportResistanceProIndicator _iSR;
        private Logger _logger;
        private PositionManager _position;
        private ScheduleManager _schedule;
        private DailyController _dailyController;
        private StrategyInterface _riskManagment, _signalManagment;
        private StrategyManager _strategyManager;
        private TelegramBot _telegram;

        protected override void OnStart()
        {
            _iSR = Indicators.GetIndicator<SupportResistanceProIndicator>(0, 1,"Orange", 0, 1, "Orange");

            _telegram = new TelegramBot(TelegramToken, TelegramChatId, this);
            _logger = new Logger(LoggerVerboseLevel, this, (UseTelegramAlerts) ? _telegram : null);
            _position = new PositionManager(null, null, null, this, _logger);

            _schedule = new ScheduleManager(_logger);
            _schedule.AddScheduler(new InclusiveSchedule(TradingStartHour, TradingStartMinute, TradingStopHour, TradingStopMinute, this));
            _dailyController = new DailyController(MaxTradesPerDay, (UseOthersFilter) ? _position.ManagerGroupLabel : null, this, _logger);

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
            return UseFirstTakeProfit && _position.Position.Pips >= FirstTakeProfitPips;
        }

        private bool FirstScalingOutAction()
        {
            return !_position.ClosePositionPartially(FirstTakeProfitParcialCloseVolumePerc) || (!UseFirstTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private bool SecondScalingOutTrigger()
        {
            return UseSecondTakeProfit && _position.Position.Pips >= SecondTakeProfitPips;
        }

        private bool SecondScalingOutAction()
        {
            return !_position.ClosePositionPartially(SecondTakeProfitParcialCloseVolumePerc) || (!UseSecondTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private bool ThirdScalingOutTrigger()
        {
            return UseThirdTakeProfit && _position.Position.Pips >= ThirdTakeProfitPips;
        }

        private bool ThirdScalingOutAction()
        {
            return !_position.ClosePositionPartially(ThirdTakeProfitParcialCloseVolumePerc) || (!UseThirdTakeProfitBreakEven) || _position.ModifyStopLossToBreakEven(false);
        }

        private void InitializeSignalManagment()
        {
            var state0 = _signalManagment.CreateStrategyState("No Position");
            var state1 = _signalManagment.CreateStrategyState("Limit Buy Position");
            var state2 = _signalManagment.CreateStrategyState("Limit Sell Position");
            var state3 = _signalManagment.CreateStrategyState("Active Position");

            state0.CreateBarTransition("Market Order Buy Signal", ControlledMarketBuyEntryTrigger, BuyAction, state3);
            state0.CreateBarTransition("Market Order Sell Signal", ControlledMarketSellEntryTrigger, SellAction, state3);
            state0.CreateBarTransition("Limit Order Buy Trigger", ControlledLimitBuyActivationTrigger, null, state1);
            state0.CreateBarTransition("Limit Order Sell Trigger", ControlledLimitSellActivationTrigger, null, state2);

            state1.CreateBarTransition("Exit Trigger", MarketSellTrigger, null, state0);
            state1.CreateTickTransition("Limit Order Buy Signal", LimitBuyEntryTrigger, BuyAction, state3);
            
            state2.CreateBarTransition("Exit Trigger", MarketBuyTrigger, null, state0);
            state2.CreateTickTransition("Limit Order Sell Signal", LimitSellEntryTrigger, SellAction, state3);
            
            state3.CreateOrderTransition("Hit Stop-Limit", HitStopLimitTrigger, null, state0);
            state3.CreateBarTransition("Hit Stop-Limit", HitStopLimitTrigger, null, state0);
            state3.CreateBarTransition("Exit Signal", MarketExitTrigger, ExitAction, state0);

            _signalManagment.LoadStrategyState(state0);
        }

        private bool MarketBuyTrigger()
        {
            return Math.Abs(_iSR.SupportLine.Last(2) - _iSR.SupportLine.Last(3)) > Symbol.PointSize && Bars.LowPrices.Last(1) > _iSR.SupportLine.Last(1) - _position.ConvertPipsToDeltaPrice(SupportTolerancePips);
        }
        
        private bool MarketSellTrigger()
        {
            return Math.Abs(_iSR.ResistanceLine.Last(2) - _iSR.ResistanceLine.Last(3)) > Symbol.PointSize && Bars.HighPrices.Last(1) < _iSR.ResistanceLine.Last(1) + _position.ConvertPipsToDeltaPrice(ResistanceTolerancePips);
        }

        private bool LimitBuyTrigger()
        {
            return Bars.ClosePrices.LastValue < _iSR.SupportLine.Last(1) + _position.ConvertPipsToDeltaPrice(SupportLimitTargetPips);
        }

        private bool LimitSellTrigger()
        {
            return Bars.ClosePrices.LastValue > _iSR.ResistanceLine.Last(1) - _position.ConvertPipsToDeltaPrice(ResistanceLimitTargetPips);
        }

        private bool ControlledMarketBuyEntryTrigger()
        {
            if (UseLimitOrders)
                return false;
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return MarketBuyTrigger();
        }

        private bool ControlledMarketSellEntryTrigger()
        {
            if (UseLimitOrders)
                return false;
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return MarketSellTrigger();
        }

        private bool MarketExitTrigger()
        {
            var ttype = _position.Position.TradeType;
            return (ttype == TradeType.Buy && MarketSellTrigger()) || (ttype == TradeType.Sell && MarketBuyTrigger());
        }

        private bool ControlledLimitBuyActivationTrigger()
        {
            if (!UseLimitOrders)
                return false;
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return MarketBuyTrigger();
        }
        
        private bool ControlledLimitSellActivationTrigger()
        {
            if (!UseLimitOrders)
                return false;
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return MarketSellTrigger();
        }

        private bool LimitBuyEntryTrigger()
        {
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return LimitBuyTrigger();
        }

        private bool LimitSellEntryTrigger()
        {
            if (UseScheduleTrading && !_schedule.IsOnSchedule())
                return false;
            if (UseDailyTradingController && !_dailyController.IsAllowedToTrade())
                return false;
            return LimitSellTrigger();
        }

        private bool HitStopLimitTrigger()
        {
            return !_position.IsCurrentlyOpened();
        }

        private bool BuyAction()
        {
            return (UseDynamicVolume) ? _position.OpenPositionPro(TradeType.Buy, DynamicVolumePerc, StopLossPips) : _position.OpenPosition(TradeType.Buy, StaticVolumeUnits, StopLossPips);
        }

        private bool SellAction()
        {
            return (UseDynamicVolume) ? _position.OpenPositionPro(TradeType.Sell, DynamicVolumePerc, StopLossPips) : _position.OpenPosition(TradeType.Sell, StaticVolumeUnits, StopLossPips);
        }

        private bool ExitAction()
        {
            return _position.ClosePositionTotally();
        }
    }
}
