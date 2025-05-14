using System;
using System.Net;
using cAlgo.API;
using cAlgo.API.Indicators;
using Telegram.Bot;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, AccessRights = AccessRights.FullAccess)]
    public class ADRPro : Indicator
    {
        [Parameter("Signal TimeFrame", Group = "ADR Settings", DefaultValue = "Daily")]
        public TimeFrame SignalTimeFrame { get; set; }
        [Parameter("Signals To Show", Group = "ADR Settings", DefaultValue = 3)]
        public int SignalsToShow { get; set; }
        [Parameter("Signals To Extend", Group = "ADR Settings", DefaultValue = 1)]
        public int SignalsToExtend { get; set; }
        [Parameter("Signal Period", Group = "ADR Settings", DefaultValue = 15, MinValue = 1)]
        public int SignalPeriod { get; set; }
        [Parameter("Signal MA Type", Group = "ADR Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SignalMaType { get; set; }
        [Parameter("Chart Alerts", Group = "Alert Settings", DefaultValue = true)]
        public bool UseCharAlerts { get; set; }
        [Parameter("Telegram Alerts", Group = "Alert Settings", DefaultValue = true)]
        public bool UseTelegramAlerts { get; set; }
        [Parameter("Telegram Token", Group = "Alert Settings", DefaultValue = "1865635880:AAGsFk2fYgJUQBndir8")]
        public string TelegramToken { get; set; }
        [Parameter("Telegram ChatId", Group = "Alert Settings", DefaultValue = "681983")]
        public string TelegramChatId { get; set; }

        private Bars _signalBars;
        private AverageTrueRange _iATR;
        private int _lastHighAlertIndex = 0;
        private int _lastLowAlertIndex = 0;

        private StackPanel _stackPanel;
        private string _documentPath;
        private string _soundAlertPath;
        private string _pathToAlertSound;

        private TelegramBotClient _telegram;

        protected override void Initialize()
        {
            _signalBars = MarketData.GetBars(SignalTimeFrame, SymbolName);
            _iATR = Indicators.AverageTrueRange(_signalBars, SignalPeriod, SignalMaType);

            InitializeChartAlerts();
            InitializeTelegramAlerts();
        }

        public override void Calculate(int index)
        {
            if (TimeFrame >= SignalTimeFrame)
                return;

            if (!IsLastBar)
                return;

            for (var i = SignalsToShow - 1; i > -1; i--)
            {
                var startTime = CalculateSignalStartDate(i);
                var stopTime = CalculateSignalStopDate(i);
                var extensionTime = CalculateSignalExtensionDate(i);
                var adr = _iATR.Result.Last(i);
                var open = _signalBars.OpenPrices.Last(i);
                var high = _signalBars.HighPrices.Last(i);
                var low = _signalBars.LowPrices.Last(i);
                var close = _signalBars.ClosePrices.Last(i);
                var highLevel = CalculateAdrHigh(adr, open, high, low, close);
                var lowLevel = CalculateAdrLow(adr, open, high, low, close);
                if (i == 0)
                {
                    if (close > highLevel)
                    {
                        DrawSignalLines(i, startTime, stopTime, extensionTime, highLevel, lowLevel, Color.IndianRed, Color.RoyalBlue, 1);
                        if (Bars.ClosePrices.HasCrossedAbove(highLevel, 1) && _lastHighAlertIndex != index)
                        {
                            DrawChartAlert("Price Crossed Above High Level at " + DateTime.UtcNow);
                            SendTelegramAlert("Price Crossed Above High Level on " + SymbolName + " at " + DateTime.UtcNow);
                            _lastHighAlertIndex = index;
                        }
                        continue;
                    }
                    if (close < lowLevel)
                    {
                        DrawSignalLines(i, startTime, stopTime, extensionTime, highLevel, lowLevel, Color.RoyalBlue, Color.IndianRed, 1);
                        if (Bars.ClosePrices.HasCrossedBelow(lowLevel, 1) && _lastLowAlertIndex != index)
                        {
                            DrawChartAlert("Price Crossed Below Low Level at " + DateTime.UtcNow);
                            SendTelegramAlert("Price Crossed Below Low Level on " + SymbolName + " at " + DateTime.UtcNow);
                            _lastLowAlertIndex = index;
                        }
                        continue;
                    }

                }
                DrawSignalLines(i, startTime, stopTime, extensionTime, highLevel, lowLevel, Color.RoyalBlue, Color.RoyalBlue, 1);
            }
        }

        private DateTime CalculateSignalStartDate(int lastIndex)
        {
            return _signalBars.OpenTimes.Last(lastIndex);
        }

        private DateTime CalculateSignalStopDate(int lastIndex)
        {
            return lastIndex - 1 < 0 ? DateTime.UtcNow : _signalBars.OpenTimes.Last(lastIndex - 1);
        }

        private DateTime CalculateSignalExtensionDate(int lastIndex)
        {
            return lastIndex - 1 - SignalsToExtend < 0 ? DateTime.UtcNow : _signalBars.OpenTimes.Last(lastIndex - 1 - SignalsToExtend);
        }

        private double CalculateAdrHigh(double adr, double open, double high, double low, double close)
        {
            return high - low < adr ? low + adr : close >= open ? low + adr : high;
        }

        private double CalculateAdrLow(double adr, double open, double high, double low, double close)
        {
            return high - low < adr ? high - adr : close >= open ? low : high - adr;
        }

        private void DrawSignalLines(int id, DateTime lineStart, DateTime lineEnd, DateTime lineExtension, double highLevel, double lowLevel, Color highLineColor, Color lowLineColor, int lineThickness)
        {
            Chart.DrawTrendLine("HighLine_" + id, lineStart, highLevel, lineEnd, highLevel, highLineColor, lineThickness, LineStyle.Solid);
            Chart.DrawTrendLine("LowLine_" + id, lineStart, lowLevel, lineEnd, lowLevel, lowLineColor, lineThickness, LineStyle.Solid);
            Chart.DrawTrendLine("HighLineExtension_" + id, lineEnd, highLevel, lineExtension, highLevel, highLineColor, lineThickness, LineStyle.DotsRare);
            Chart.DrawTrendLine("LowLineExtension_" + id, lineEnd, lowLevel, lineExtension, lowLevel, lowLineColor, lineThickness, LineStyle.DotsRare);
        }

        private void InitializeChartAlerts()
        {
            if (!UseCharAlerts)
                return;
            _documentPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            _soundAlertPath = "alert.mp3";
            _pathToAlertSound = string.Format("{0}\\cAlgo\\Sources\\Indicators\\ADR Pro\\Sounds\\{1}", _documentPath, _soundAlertPath);
            _stackPanel = new StackPanel 
            {
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Bottom,
                IsVisible = true,
                IsEnabled = false,
                Height = 23
            };
            var button = new Button 
            {
                Text = "Clear Alert"
            };
            button.Click += ClearChartAlert;
            _stackPanel.AddChild(button);
            Chart.AddControl(_stackPanel);
        }

        private void DrawChartAlert(string message)
        {
            if (!UseCharAlerts)
                return;
            Notifications.PlaySound(_pathToAlertSound);
            Chart.DrawStaticText("AlertText", message, VerticalAlignment.Center, HorizontalAlignment.Center, Color.White);
            _stackPanel.IsEnabled = true;
        }

        private void ClearChartAlert(ButtonClickEventArgs args)
        {
            Chart.RemoveObject("AlertText");
            _stackPanel.IsEnabled = false;
        }

        private void InitializeTelegramAlerts()
        {
            if (!UseTelegramAlerts)
                return;
            ServicePointManager.Expect100Continue = true;
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
            _telegram = new TelegramBotClient(TelegramToken);
        }

        private void SendTelegramAlert(string message)
        {
            Print("Sent Telegram!");
            if (UseTelegramAlerts)
                _telegram.SendTextMessageAsync(TelegramChatId, message);
        }
    }
}
