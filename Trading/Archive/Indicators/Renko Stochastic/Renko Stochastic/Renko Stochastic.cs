using System;
using System.Net;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.Internet)]
    public class RenkoStochastic : Indicator
    {
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

        [Parameter("Draw Buy Icon", Group = "Drawing Settings", DefaultValue = true)]
        public bool DrawBuyIcon { get; set; }
        [Parameter("Draw Sell Icon", Group = "Drawing Settings", DefaultValue = true)]
        public bool DrawSellIcon { get; set; }
        [Parameter("Buy Icon Type", Group = "Drawing Settings", DefaultValue = ChartIconType.UpArrow)]
        public ChartIconType BuyIconType { get; set; }
        [Parameter("Sell Icon Type", Group = "Drawing Settings", DefaultValue = ChartIconType.DownArrow)]
        public ChartIconType SellIconType { get; set; }
        [Parameter("Buy Icon Color", Group = "Drawing Settings", DefaultValue = "RoyalBlue")]
        public string BuyIconColor { get; set; }
        [Parameter("Sell Icon Color", Group = "Drawing Settings", DefaultValue = "IndianRed")]
        public string SellIconColor { get; set; }
        [Parameter("Buy Icon Distance (Pips)", Group = "Drawing Settings", DefaultValue = 5, Step = 0.1)]
        public double BuyIconDistance { get; set; }
        [Parameter("Sell Icon Distance (Pips)", Group = "Drawing Settings", DefaultValue = 5, Step = 0.1)]
        public double SellIconDistance { get; set; }

        [Parameter("Enable", Group = "Telegram Alerts Settings", DefaultValue = false)]
        public bool SendTelegramAlerts { get; set; }
        [Parameter("Token", Group = "Telegram Alerts Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("ChatId", Group = "Telegram Alerts Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        private StochasticOscillator _iSto;
        private Color _buyIconColor, _sellIconColor;
        private TelegramBot _telegram;
        private int _lastAlertIndex;

        protected override void Initialize()
        {
            _iSto = Indicators.StochasticOscillator(StoKPeriod, StoKSlowing, StoDPeriod, StoMaType);
            _buyIconColor = Color.FromName(BuyIconColor);
            _sellIconColor = Color.FromName(SellIconColor);
            _telegram = new TelegramBot(TelegramToken, TelegramChatId, Symbol.Name, TimeFrame.Name);
        }

        public override void Calculate(int index)
        {
            if (Bars.ClosePrices.Last(3) > Bars.ClosePrices.Last(2) && Bars.ClosePrices.Last(2) < Bars.ClosePrices.Last(1) && _iSto.PercentD.Last(1) < StoOversoldLevel && _iSto.PercentK.Last(1) < StoOversoldLevel && Bars.HighPrices.Last(0) > Bars.HighPrices.Last(1))
            {
                if (DrawBuyIcon)
                    Chart.DrawIcon("Buy_" + index, BuyIconType, Bars.OpenTimes[index], Bars.LowPrices[index] - BuyIconDistance * Symbol.PipSize, _buyIconColor);
                if (SendTelegramAlerts && IsLastBar && _lastAlertIndex != index)
                {
                    _telegram.SendTextMessage("Oversold Buy Signal Alert");
                    _lastAlertIndex = index;
                }

            }
            if (Bars.ClosePrices.Last(3) < Bars.ClosePrices.Last(2) && Bars.ClosePrices.Last(2) > Bars.ClosePrices.Last(1) && _iSto.PercentD.Last(1) > StoOverboughtLevel && _iSto.PercentK.Last(1) > StoOverboughtLevel && Bars.HighPrices.Last(0) < Bars.HighPrices.Last(1))
            {
                if (DrawSellIcon)
                    Chart.DrawIcon("Sell_" + index, SellIconType, Bars.OpenTimes[index], Bars.HighPrices[index] + SellIconDistance * Symbol.PipSize, _sellIconColor);
                if (SendTelegramAlerts && IsLastBar && _lastAlertIndex != index)
                {
                    _telegram.SendTextMessage("Overbought Sell Signal Alert");
                    _lastAlertIndex = index;
                }

            }
        }
    }

    public class TelegramBot
    {
        private readonly string _defaultUrl;

        public TelegramBot(string token, string defaultChatId, string symbol, string timeframe)
        {
            _defaultUrl = string.Format("https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text=[{2}-{3}] ", token, defaultChatId, symbol, timeframe);
            ServicePointManager.Expect100Continue = true;
            ServicePointManager.DefaultConnectionLimit = 1000000;
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        }

        public void SendTextMessage(string message)
        {
            WebRequest.Create(_defaultUrl + message).GetResponse();
        }
    }
}
