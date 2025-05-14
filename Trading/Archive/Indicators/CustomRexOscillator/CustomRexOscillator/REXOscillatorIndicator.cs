using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomRexOscillator : Indicator
    {
        [Parameter("OpenSource")]
        public DataSeries OpenSource { get; set; }
        [Parameter("HighSource")]
        public DataSeries HighSource { get; set; }
        [Parameter("LowSource")]
        public DataSeries LowSource { get; set; }
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("Period", DefaultValue = 14)]
        public int SignalPeriod { get; set; }
        [Parameter("Smoothing Period", DefaultValue = 14)]
        public int SmoothingPeriod { get; set; }
        [Parameter("MA Type", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "Green", Thickness = 1)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Red", Thickness = 1)]
        public IndicatorDataSeries DownLine { get; set; }

        private IndicatorDataSeries _tvbDS;

        protected override void Initialize()
        {
            _tvbDS = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            _tvbDS[index] = 3 * CloseSource[index] - (LowSource[index] + OpenSource[index] + HighSource[index]);
            UpLine[index] = Indicators.MovingAverage(_tvbDS, SmoothingPeriod, MAType).Result[index] / Symbol.PipSize;
            DownLine[index] = Indicators.MovingAverage(UpLine, SignalPeriod, MAType).Result[index];
        }
    }

}
