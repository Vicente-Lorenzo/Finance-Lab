using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomHLCTrend : Indicator
    {
        [Parameter("HighSource")]
        public DataSeries HighSource { get; set; }
        [Parameter("LowSource")]
        public DataSeries LowSource { get; set; }
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("High Period", DefaultValue = 34, MinValue = 1)]
        public int HighPeriod { get; set; }
        [Parameter("Low Period", DefaultValue = 13, MinValue = 1)]
        public int LowPeriod { get; set; }
        [Parameter("Close Period", DefaultValue = 5, MinValue = 1)]
        public int ClosePeriod { get; set; }
        [Parameter("Moving Average Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "White", Thickness = 1)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Blue", Thickness = 1)]
        public IndicatorDataSeries DownLine { get; set; }

        private MovingAverage _closeMA, _highMA, _lowMA;

        protected override void Initialize()
        {
            _closeMA = Indicators.MovingAverage(CloseSource, ClosePeriod, MAType);
            _highMA = Indicators.MovingAverage(HighSource, HighPeriod, MAType);
            _lowMA = Indicators.MovingAverage(LowSource, LowPeriod, MAType);
        }

        public override void Calculate(int index)
        {
            UpLine[index] = _closeMA.Result[index] - _highMA.Result[index];
            DownLine[index] = _lowMA.Result[index] - _closeMA.Result[index];
        }
    }
}
