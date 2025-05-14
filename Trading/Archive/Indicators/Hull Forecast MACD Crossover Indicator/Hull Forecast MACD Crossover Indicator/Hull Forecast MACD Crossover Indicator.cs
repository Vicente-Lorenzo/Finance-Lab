using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class HullForecastMACDCrossoverIndicator : Indicator
    {
        [Parameter("Source Price", Group = "Hull General Settings")]
        public DataSeries HullSourcePrice { get; set; }
        [Parameter("Coverage Period", Group = "Hull General Settings", DefaultValue = 35)]
        public int HullCoveragePeriod { get; set; }
        [Parameter("Coverage Period Devisor", Group = "Hull General Settings", DefaultValue = 1.7)]
        public double HullPeriodDivisor { get; set; }
        [Parameter("Line Draw Level", Group = "Hull General Settings", DefaultValue = 0.0, Step = 1E-05)]
        public double HullLineDrawLevel { get; set; }

        [Parameter("Source Price", Group = "MACD General Settings")]
        public DataSeries MacdSourcePrice { get; set; }
        [Parameter("MA Type", Group = "MACD General Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MaType { get; set; }
        [Parameter("Long Cycle", Group = "MACD General Settings", DefaultValue = 26)]
        public int LongCycle { get; set; }
        [Parameter("Short Cycle", Group = "MACD General Settings", DefaultValue = 12)]
        public int ShortCycle { get; set; }
        [Parameter("Signal Periods", Group = "MACD General Settings", DefaultValue = 9)]
        public int Periods { get; set; }

        [Parameter("Smoothing MA Period (0 to Disable)", Group = "MACD Reaction Settings", DefaultValue = 0, MinValue = 0)]
        public int SmoothPeriod { get; set; }
        [Parameter("Smoothing MA Type", Group = "MACD Reaction Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SmoothMaType { get; set; }
        [Parameter("Enable Zero Lag", Group = "MACD Reaction Settings", DefaultValue = false)]
        public bool UseZeroLag { get; set; }

        [Parameter("Overbought Level", Group = "MACD Level Settings", DefaultValue = 0.0004, Step = 1E-05)]
        public double OverboughtLevel { get; set; }
        [Parameter("Oversold Level", Group = "MACD Level Settings", DefaultValue = -0.0004, Step = 1E-05)]
        public double OversoldLevel { get; set; }

        [Parameter("Draw Buy Signal", Group = "Chart Signal Settings", DefaultValue = true)]
        public bool DrawChartBuySignal { get; set; }
        [Parameter("Draw Sell Signal", Group = "Chart Signal Settings", DefaultValue = true)]
        public bool DrawChartSellSignal { get; set; }
        [Parameter("Buy Signal Color", Group = "Chart Signal Settings", DefaultValue = "RoyalBlue")]
        public string BuyChartSignalColor { get; set; }
        [Parameter("Sell Signal Color", Group = "Chart Signal Settings", DefaultValue = "IndianRed")]
        public string SellChartSignalColor { get; set; }
        [Parameter("Buy Icon Type", Group = "Chart Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType BuyChartIconType { get; set; }
        [Parameter("Sell Icon Type", Group = "Chart Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType SellChartIconType { get; set; }
        [Parameter("Icon Distance", Group = "Chart Signal Settings", DefaultValue = 0.0005, Step = 0.0001)]
        public double ChartDistance { get; set; }

        [Parameter("Draw Buy Signal", Group = "Indicator Signal Settings", DefaultValue = true)]
        public bool DrawIndicatorBuySignal { get; set; }
        [Parameter("Draw Sell Signal", Group = "Indicator Signal Settings", DefaultValue = true)]
        public bool DrawIndicatorSellSignal { get; set; }
        [Parameter("Buy Signal Color", Group = "Indicator Signal Settings", DefaultValue = "RoyalBlue")]
        public string BuyIndicatorSignalColor { get; set; }
        [Parameter("Sell Signal Color", Group = "Indicator Signal Settings", DefaultValue = "IndianRed")]
        public string SellIndicatorSignalColor { get; set; }
        [Parameter("Buy Icon Type", Group = "Indicator Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType BuyIndicatorIconType { get; set; }
        [Parameter("Sell Icon Type", Group = "Indicator Signal Settings", DefaultValue = ChartIconType.Circle)]
        public ChartIconType SellIndicatorIconType { get; set; }
        [Parameter("Icon Distance", Group = "Indicator Signal Settings", DefaultValue = 0.0001, Step = 0.0001)]
        public double IndicatorDistance { get; set; }

        [Output("Hull Up Trend Line", PlotType = PlotType.DiscontinuousLine, LineColor = "RoyalBlue", Thickness = 5)]
        public IndicatorDataSeries HullUpLine { get; set; }
        [Output("Hull Down Trend Line", PlotType = PlotType.DiscontinuousLine, LineColor = "IndianRed", Thickness = 5)]
        public IndicatorDataSeries HullDownLine { get; set; }

        [Output("MACD", LineColor = "Gray", PlotType = PlotType.DiscontinuousLine, LineStyle = LineStyle.Solid, Thickness = 2)]
        public IndicatorDataSeries MacdLine { get; set; }
        [Output("MACD Rising", LineColor = "Blue", PlotType = PlotType.DiscontinuousLine, LineStyle = LineStyle.Solid, Thickness = 2)]
        public IndicatorDataSeries MacdRisingLine { get; set; }
        [Output("MACD Falling", LineColor = "Red", PlotType = PlotType.DiscontinuousLine, LineStyle = LineStyle.Solid, Thickness = 2)]
        public IndicatorDataSeries MacdFallingLine { get; set; }
        [Output("Signal Line", LineColor = "Yellow", PlotType = PlotType.DiscontinuousLine, LineStyle = LineStyle.Lines, Thickness = 1)]
        public IndicatorDataSeries SignalLine { get; set; }

        [Output("Overbought Level", LineColor = "Silver", LineStyle = LineStyle.Dots, PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries OverboughtLine { get; set; }
        [Output("Oversold Level", LineColor = "Silver", LineStyle = LineStyle.Dots, PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries OversoldLine { get; set; }

        [Output("Positive Histogram", PlotType = PlotType.Histogram, LineColor = "Aquamarine", Thickness = 5)]
        public IndicatorDataSeries HistogramPositive { get; set; }
        [Output("Overbought Rising Histogram", PlotType = PlotType.Histogram, LineColor = "Green", Thickness = 5)]
        public IndicatorDataSeries HistogramOverboughtRising { get; set; }
        [Output("Overbought Falling Histogram", PlotType = PlotType.Histogram, LineColor = "DeepSkyBlue", Thickness = 5)]
        public IndicatorDataSeries HistogramOverboughtFalling { get; set; }
        [Output("Negative Histogram", PlotType = PlotType.Histogram, LineColor = "Pink", Thickness = 5)]
        public IndicatorDataSeries HistogramNegative { get; set; }
        [Output("Oversold Rising Histogram", PlotType = PlotType.Histogram, LineColor = "Red", Thickness = 5)]
        public IndicatorDataSeries HistogramOversoldRising { get; set; }
        [Output("Oversold Falling Histogram", PlotType = PlotType.Histogram, LineColor = "DarkRed", Thickness = 5)]
        public IndicatorDataSeries HistogramOversoldFalling { get; set; }

        private HullMovingAverage _ma1, _ma2, _ma3;
        private IndicatorDataSeries _auxValues;
        private Color _buyIndicatorSignalColor, _sellIndicatorSignalColor, _buyChartSignalColor, _sellChartSignalColor;

        private MovingAverage _slowMa, _fastMa, _signalMa, _smoothedSlowMa, _smoothedFastMa, _smoothedMacd, _smoothedSignalMa;
        private IndicatorDataSeries _macd, _auxHistogram;

        private void InitializeHullForecast()
        {
            _auxValues = CreateDataSeries();

            _ma1 = Indicators.HullMovingAverage(HullSourcePrice, (int)Math.Floor(HullCoveragePeriod / HullPeriodDivisor));
            _ma2 = Indicators.HullMovingAverage(HullSourcePrice, HullCoveragePeriod);
            _ma3 = Indicators.HullMovingAverage(_auxValues, (int)Math.Floor(Math.Sqrt(HullCoveragePeriod)));

            _buyChartSignalColor = Color.FromName(BuyChartSignalColor);
            _sellChartSignalColor = Color.FromName(SellChartSignalColor);
            _buyIndicatorSignalColor = Color.FromName(BuyIndicatorSignalColor);
            _sellIndicatorSignalColor = Color.FromName(SellIndicatorSignalColor);
        }

        private void InitializeMacdCrossover()
        {
            _slowMa = Indicators.MovingAverage(MacdSourcePrice, LongCycle, MaType);
            _fastMa = Indicators.MovingAverage(MacdSourcePrice, ShortCycle, MaType);
            _macd = CreateDataSeries();
            _signalMa = Indicators.MovingAverage(_macd, Periods, MaType);

            _smoothedSlowMa = Indicators.MovingAverage(_slowMa.Result, LongCycle, MaType);
            _smoothedFastMa = Indicators.MovingAverage(_fastMa.Result, ShortCycle, MaType);
            _smoothedMacd = Indicators.MovingAverage(_macd, SmoothPeriod, SmoothMaType);
            _smoothedSignalMa = Indicators.MovingAverage(_signalMa.Result, SmoothPeriod, SmoothMaType);

            _auxHistogram = CreateDataSeries();
        }

        protected override void Initialize()
        {
            InitializeHullForecast();
            InitializeMacdCrossover();
        }

        private void CalculateHullForecast(int index)
        {
            _auxValues[index] = 2.0 * _ma1.Result[index] - _ma2.Result[index];

            if (_ma3.Result[index] > _ma3.Result[index - 1])
            {
                HullUpLine[index] = HullLineDrawLevel;
                HullUpLine[index - 1] = HullLineDrawLevel;
                HullDownLine[index] = double.NaN;
            }
            else if (_ma3.Result[index] < _ma3.Result[index - 1])
            {
                HullDownLine[index] = HullLineDrawLevel;
                HullDownLine[index - 1] = HullLineDrawLevel;
                HullUpLine[index] = double.NaN;
            }
        }

        private void CalculateMacdCrossover(int index)
        {
            _macd[index] = UseZeroLag ? (_fastMa.Result[index] * 2 - _smoothedFastMa.Result[index]) - (_slowMa.Result[index] * 2 - _smoothedSlowMa.Result[index]) : _fastMa.Result[index] - _slowMa.Result[index];
            MacdLine[index] = SmoothPeriod > 0 ? _smoothedMacd.Result[index] : _macd[index];
            SignalLine[index] = SmoothPeriod > 0 ? _smoothedSignalMa.Result[index] : _signalMa.Result[index];
            if (MacdLine.IsRising())
                MacdRisingLine[index] = SmoothPeriod > 0 ? _smoothedMacd.Result[index] : _macd[index];
            if (MacdLine.IsFalling())
                MacdFallingLine[index] = SmoothPeriod > 0 ? _smoothedMacd.Result[index] : _macd[index];
            OverboughtLine[index] = OverboughtLevel;
            OversoldLine[index] = OversoldLevel;

            var currentHistogram = MacdLine[index] - SignalLine[index];
            _auxHistogram[index] = currentHistogram;
            if (currentHistogram > 0)
            {
                if (currentHistogram > OverboughtLevel)
                {
                    if (_auxHistogram.IsRising())
                        HistogramOverboughtRising[index] = currentHistogram;
                    if (_auxHistogram.IsFalling())
                        HistogramOverboughtFalling[index] = currentHistogram;
                }
                else
                    HistogramPositive[index] = currentHistogram;
            }
            else if (currentHistogram < 0)
            {
                if (currentHistogram < OversoldLevel)
                {
                    if (_auxHistogram.IsRising())
                        HistogramOversoldRising[index] = currentHistogram;
                    if (_auxHistogram.IsFalling())
                        HistogramOversoldFalling[index] = currentHistogram;
                }
                else
                {
                    HistogramNegative[index] = currentHistogram;
                }
            }
        }

        public override void Calculate(int index)
        {
            CalculateHullForecast(index);
            CalculateMacdCrossover(index);

            if (!double.IsNaN(HullUpLine[index - 1]) && MacdLine[index - 1] < OversoldLevel && SignalLine[index - 1] < MacdLine[index - 1] && SignalLine[index - 2] > MacdLine[index - 2])
            {
                if (DrawChartBuySignal)
                    Chart.DrawIcon("ChartBuy_" + (index - 1), BuyChartIconType, Bars.OpenTimes[index - 1], Bars.LowPrices[index - 1] - ChartDistance, _buyChartSignalColor);
                if (DrawIndicatorBuySignal)
                    IndicatorArea.DrawIcon("IndicatorBuy_" + (index - 1), BuyIndicatorIconType, Bars.OpenTimes[index - 1], MacdLine[index - 1] < SignalLine[index - 1] ? MacdLine[index - 1] - IndicatorDistance : SignalLine[index - 1] - IndicatorDistance, _buyIndicatorSignalColor);
            }

            if (!double.IsNaN(HullDownLine[index - 1]) && MacdLine[index - 1] > OverboughtLevel && SignalLine[index - 1] > MacdLine[index - 1] && SignalLine[index - 2] < MacdLine[index - 2])
            {
                if (DrawChartSellSignal)
                    Chart.DrawIcon("ChartSell_" + (index - 1), SellChartIconType, Bars.OpenTimes[index - 1], Bars.HighPrices[index - 1] + ChartDistance, _sellChartSignalColor);
                if (DrawIndicatorSellSignal)
                    IndicatorArea.DrawIcon("IndicatorSell_" + (index - 1), SellIndicatorIconType, Bars.OpenTimes[index - 1], MacdLine[index - 1] > SignalLine[index - 1] ? MacdLine[index - 1] + IndicatorDistance : SignalLine[index - 1] + IndicatorDistance, _sellIndicatorSignalColor);
            }

        }

    }
}
