using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomAbsoluteStrenghtLines : Indicator
    {
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("Period", DefaultValue = 7, MinValue = 1)]
        public int Period { get; set; }
        [Parameter("Smoothing Period", DefaultValue = 2, MinValue = 1)]
        public int SmoothingPeriod { get; set; }
        [Parameter("Moving Average Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "Blue", Thickness = 1)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Red", Thickness = 1)]
        public IndicatorDataSeries DownLine { get; set; }

        public IndicatorDataSeries _bullsDS, _bearsDS;
        public MovingAverage _bullsMA, _bearsMA, _smoothedBullsMA, _smoothedBearsMA;

        protected override void Initialize()
        {
            _bullsDS = CreateDataSeries();
            _bearsDS = CreateDataSeries();

            _bullsMA = Indicators.MovingAverage(_bullsDS, Period, MAType);
            _bearsMA = Indicators.MovingAverage(_bearsDS, Period, MAType);

            _smoothedBullsMA = Indicators.MovingAverage(_bullsMA.Result, SmoothingPeriod, MAType);
            _smoothedBearsMA = Indicators.MovingAverage(_bearsMA.Result, SmoothingPeriod, MAType);
        }

        public override void Calculate(int index)
        {
            double NewPrice = CloseSource[index];
            double OldPrice = CloseSource[index - 1];

            _bullsDS[index] = 0.5 * (Math.Abs(NewPrice - OldPrice) + (NewPrice - OldPrice));
            _bearsDS[index] = 0.5 * (Math.Abs(NewPrice - OldPrice) - (NewPrice - OldPrice));

            UpLine[index] = _smoothedBullsMA.Result[index];
            DownLine[index] = _smoothedBearsMA.Result[index];
        }
    }
}
