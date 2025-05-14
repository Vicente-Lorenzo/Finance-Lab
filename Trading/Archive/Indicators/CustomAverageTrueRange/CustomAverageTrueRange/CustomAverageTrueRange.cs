using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomAverageTrueRange : Indicator
    {
        [Parameter("HighSource")]
        public DataSeries HighSource { get; set; }
        [Parameter("LowSource")]
        public DataSeries LowSource { get; set; }
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("Period", DefaultValue = 14)]
        public int Period { get; set; }
        [Parameter("Moving Average Type", DefaultValue = 14)]
        public MovingAverageType MAType { get; set; }
        [Output("Result", LineColor = "Red", Thickness = 1)]
        public IndicatorDataSeries Result { get; set; }

        private MovingAverage _atrMA;
        private IndicatorDataSeries _tempDS;

        protected override void Initialize()
        {
            _tempDS = CreateDataSeries();
            _atrMA = Indicators.MovingAverage(_tempDS, Period, MAType);
        }

        public override void Calculate(int index)
        {
            double high = HighSource[index];
            double low = LowSource[index];

            if (index == 0)
            {
                _tempDS[index] = high - low;
            }
            else
            {
                double prevClose = CloseSource[index - 1];
                _tempDS[index] = Math.Max(high, prevClose) - Math.Min(low, prevClose);
            }

            Result[index] = _atrMA.Result[index];
        }
    }
}
