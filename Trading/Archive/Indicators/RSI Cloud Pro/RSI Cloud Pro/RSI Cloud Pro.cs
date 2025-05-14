using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo.Indicators
{
    [Cloud("OB1 Level", "OB2 Level")]
    [Cloud("OS1 Level", "OS2 Level")]
    [Cloud("RSI", "MA")]
    [Indicator(IsOverlay = false, AccessRights = AccessRights.None)]
    public class RSICloudPro : Indicator
    {
        [Parameter("Period", Group = "RSI Settings", DefaultValue = 14)]
        public int rsiPeriod { get; set; }
        [Parameter("Smooth", Group = "RSI Settings", DefaultValue = false)]
        public bool Smooth { get; set; }
        [Parameter("Smooth Period", Group = "RSI Settings", DefaultValue = 4)]
        public int SmoothPeriod { get; set; }
        [Parameter("Smooth Type", Group = "RSI Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType SmoothType { get; set; }

        [Parameter("OS1 Level", Group = "Levels Settings", DefaultValue = 30)]
        public int OS1_value { get; set; }
        [Parameter("OS2 Level", Group = "Levels Settings", DefaultValue = 20)]
        public int OS2_value { get; set; }
        [Parameter("OB1 Level", Group = "Levels Settings", DefaultValue = 70)]
        public int OB1_value { get; set; }
        [Parameter("OB2 Level", Group = "Levels Settings", DefaultValue = 80)]
        public int OB2_value { get; set; }

        [Parameter("Show", Group = "MA Settings", DefaultValue = true)]
        public bool maShow { get; set; }
        [Parameter("Type", Group = "MA Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MAType { get; set; }
        [Parameter("Period", Group = "MA Settings", DefaultValue = 20)]
        public int maPeriod { get; set; }

        [Parameter("Draw Buy Signal", Group = "Signal Settings", DefaultValue = true)]
        public bool DrawBuySignal { get; set; }
        [Parameter("Buy Signal Color", Group = "Signal Settings", DefaultValue = "Green")]
        public string BuySignalColor { get; set; }
        [Parameter("Draw Sell Signal", Group = "Signal Settings", DefaultValue = true)]
        public bool DrawSellSignal { get; set; }
        [Parameter("Sell Signal Color", Group = "Signal Settings", DefaultValue = "Red")]
        public string SellSignalColor { get; set; }
        [Parameter("Buy Icon Type", Group = "Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType BuyIconType { get; set; }
        [Parameter("Sell Icon Type", Group = "Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType SellIconType { get; set; }
        [Parameter("Icon Distance (Pips)", Group = "Signal Settings", DefaultValue = 10, MinValue = 1)]
        public int PipsDistance { get; set; }

        [Output("OB1 Level", LineColor = "DarkRed", LineStyle = LineStyle.Dots, Thickness = 1)]
        public IndicatorDataSeries OB1_level { get; set; }
        [Output("OB2 Level", LineColor = "DarkRed", LineStyle = LineStyle.Dots, Thickness = 1)]
        public IndicatorDataSeries OB2_level { get; set; }
        [Output("OS1 Level", LineColor = "DarkGreen", LineStyle = LineStyle.Dots, Thickness = 1)]
        public IndicatorDataSeries OS1_level { get; set; }
        [Output("OS2 Level", LineColor = "DarkGreen", LineStyle = LineStyle.Dots, Thickness = 1)]
        public IndicatorDataSeries OS2_level { get; set; }
        [Output("Mid Level", LineColor = "DimGray", LineStyle = LineStyle.Solid, Thickness = 1)]
        public IndicatorDataSeries midlevel { get; set; }
        [Output("RSI", LineColor = "Green", PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries RSIResult { get; set; }
        [Output("MA", LineColor = "Red")]
        public IndicatorDataSeries MAofRSI { get; set; }

        private MovingAverage _ma;
        private RelativeStrengthIndex _rsi;
        private MovingAverage _rsismooth;
        private Color _buySignalColor, _sellSignalColor;

        protected override void Initialize()
        {
            DataSeries _ds = Bars.TypicalPrices;

            _rsi = Indicators.RelativeStrengthIndex(_ds, rsiPeriod);
            _rsismooth = Indicators.MovingAverage(_rsi.Result, SmoothPeriod, SmoothType);
            _ma = Indicators.MovingAverage(_rsi.Result, maPeriod, MAType);

            _buySignalColor = Color.FromName(BuySignalColor);
            _sellSignalColor = Color.FromName(SellSignalColor);
        }

        public override void Calculate(int index)
        {
            OS1_level[index] = OS1_value;
            OS2_level[index] = OS2_value;
            OB1_level[index] = OB1_value;
            OB2_level[index] = OB2_value;
            midlevel[index] = 50;

            if (Smooth)
                RSIResult[index] = _rsismooth.Result[index];
            else
                RSIResult[index] = _rsi.Result[index];

            if (maShow)
                MAofRSI[index] = _ma.Result[index];

            if (RSIResult[index - 1] < MAofRSI[index - 1] && RSIResult[index] > MAofRSI[index])
                Chart.DrawIcon("Icon_" + index, BuyIconType, Bars.OpenTimes[index], Bars.LowPrices[index] - PipsDistance * Symbol.PipSize, _buySignalColor);

            if (RSIResult[index - 1] > MAofRSI[index - 1] && RSIResult[index] < MAofRSI[index])
                Chart.DrawIcon("Icon_" + index, SellIconType, Bars.OpenTimes[index], Bars.HighPrices[index] + PipsDistance * Symbol.PipSize, _sellSignalColor);
        }
    }
}
