using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class MovingAverageIndicator : Indicator
    {
        [Parameter("Source", Group = "Indicator Settings")]
        public DataSeries Source { get; set; }
        [Parameter("Period", Group = "Indicator Settings", DefaultValue = 15, MinValue = 1)]
        public int Period { get; set; }
        [Parameter("Ma Type", Group = "Indicator Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MaType { get; set; }

        [Output("Up Trend", LineColor = "RoyalBlue", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries UpTrend { get; set; }
        [Output("Unknown Trend", LineColor = "Gray", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries UnknownTrend { get; set; }
        [Output("Down Trend", LineColor = "IndianRed", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries DownTrend { get; set; }

        private MovingAverage _iMA;

        protected override void Initialize()
        {
            _iMA = Indicators.MovingAverage(Source, Period, MaType);
        }

        public override void Calculate(int index)
        {
            if (Bars.ClosePrices[index] > _iMA.Result[index])
            {
                UpTrend[index - 1] = _iMA.Result[index - 1];
                UpTrend[index] = _iMA.Result[index];
            }
            else if (Bars.ClosePrices[index] < _iMA.Result[index])
            {
                DownTrend[index - 1] = _iMA.Result[index - 1];
                DownTrend[index] = _iMA.Result[index];
            }
            else
            {
                UnknownTrend[index - 1] = _iMA.Result[index - 1];
                UnknownTrend[index] = _iMA.Result[index];
            }

        }
    }
}
