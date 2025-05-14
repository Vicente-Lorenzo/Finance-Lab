using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class MACDCrossover : Indicator
    {
        [Parameter("Source Price", Group = "General Settings")]
        public DataSeries SourcePrice { get; set; }
        [Parameter("MA Type", Group = "General Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MaType { get; set; }
        [Parameter("Long Cycle", Group = "General Settings", DefaultValue = 26)]
        public int LongCycle { get; set; }
        [Parameter("Short Cycle", Group = "General Settings", DefaultValue = 12)]
        public int ShortCycle { get; set; }
        [Parameter("Signal Periods", Group = "General Settings", DefaultValue = 9)]
        public int Periods { get; set; }

        [Parameter("Smoothing MA Period (0 to Disable)", Group = "Reaction Settings", DefaultValue = 0, MinValue = 0)]
        public int SmoothPeriod { get; set; }
        [Parameter("Smoothing MA Type", Group = "Reaction Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SmoothMaType { get; set; }
        [Parameter("Enable Zero Lag", Group = "Reaction Settings", DefaultValue = false)]
        public bool UseZeroLag { get; set; }

        [Parameter("Overbought Level", Group = "Level Settings", DefaultValue = 0.0004, Step = 1E-05)]
        public double OverboughtLevel { get; set; }
        [Parameter("Oversold Level", Group = "Level Settings", DefaultValue = -0.0004, Step = 1E-05)]
        public double OversoldLevel { get; set; }

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

        [Output("Histogram Positive", PlotType = PlotType.Histogram, LineColor = "Aquamarine", Thickness = 5)]
        public IndicatorDataSeries HistogramPositive { get; set; }
        [Output("Histogram Overbought Rising", PlotType = PlotType.Histogram, LineColor = "Green", Thickness = 5)]
        public IndicatorDataSeries HistogramOverboughtRising { get; set; }
        [Output("Histogram Overbought Falling", PlotType = PlotType.Histogram, LineColor = "DeepSkyBlue", Thickness = 5)]
        public IndicatorDataSeries HistogramOverboughtFalling { get; set; }
        [Output("Histogram Negative", PlotType = PlotType.Histogram, LineColor = "Pink", Thickness = 5)]
        public IndicatorDataSeries HistogramNegative { get; set; }
        [Output("Histogram Oversold Rising", PlotType = PlotType.Histogram, LineColor = "Red", Thickness = 5)]
        public IndicatorDataSeries HistogramOversoldRising { get; set; }
        [Output("Histogram Oversold Falling", PlotType = PlotType.Histogram, LineColor = "DarkRed", Thickness = 5)]
        public IndicatorDataSeries HistogramOversoldFalling { get; set; }

        private MovingAverage _slowMa;
        private MovingAverage _fastMa;
        private IndicatorDataSeries _macd;
        private MovingAverage _signalMa;

        private MovingAverage _smoothedSlowMa;
        private MovingAverage _smoothedFastMa;
        private MovingAverage _smoothedMacd;
        private MovingAverage _smoothedSignalMa;

        private IndicatorDataSeries _auxHistogram;

        protected override void Initialize()
        {
            _slowMa = Indicators.MovingAverage(SourcePrice, LongCycle, MaType);
            _fastMa = Indicators.MovingAverage(SourcePrice, ShortCycle, MaType);
            _macd = CreateDataSeries();
            _signalMa = Indicators.MovingAverage(_macd, Periods, MaType);

            _smoothedSlowMa = Indicators.MovingAverage(_slowMa.Result, LongCycle, MaType);
            _smoothedFastMa = Indicators.MovingAverage(_fastMa.Result, ShortCycle, MaType);
            _smoothedMacd = Indicators.MovingAverage(_macd, SmoothPeriod, SmoothMaType);
            _smoothedSignalMa = Indicators.MovingAverage(_signalMa.Result, SmoothPeriod, SmoothMaType);

            _auxHistogram = CreateDataSeries();
        }

        public override void Calculate(int index)
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

            _auxHistogram[index] = MacdLine[index] - SignalLine[index];
            if (_auxHistogram[index] > 0)
            {
                if (_auxHistogram[index] > OverboughtLevel)
                {
                    if (_auxHistogram.IsRising())
                        HistogramOverboughtRising[index] = _auxHistogram[index];
                    if (_auxHistogram.IsFalling())
                        HistogramOverboughtFalling[index] = _auxHistogram[index];
                }
                else
                    HistogramPositive[index] = _auxHistogram[index];
            }
            else if (_auxHistogram[index] < 0)
            {
                if (_auxHistogram[index] < OversoldLevel)
                {
                    if (_auxHistogram.IsRising())
                        HistogramOversoldRising[index] = _auxHistogram[index];
                    if (_auxHistogram.IsFalling())
                        HistogramOversoldFalling[index] = _auxHistogram[index];
                }
                else
                {
                    HistogramNegative[index] = _auxHistogram[index];
                }
            }
        }
    }
}
