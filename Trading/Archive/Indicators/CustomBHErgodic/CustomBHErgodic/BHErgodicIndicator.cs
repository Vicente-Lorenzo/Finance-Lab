using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, ScalePrecision = 4, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomBHErgodic : Indicator
    {
        [Parameter("CloseSource")]
        public DataSeries Source { get; set; }
        [Parameter("Short Period", DefaultValue = 2, MinValue = 1)]
        public int ShortPeriod { get; set; }
        [Parameter("Long Period", DefaultValue = 10, MinValue = 1)]
        public int LongPeriod { get; set; }
        [Parameter("Signal Period", DefaultValue = 5, MinValue = 1)]
        public int SignalPeriod { get; set; }
        [Parameter("Trigger Period", DefaultValue = 3, MinValue = 1)]
        public int TriggerPeriod { get; set; }
        [Parameter("Moving Average Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "LimeGreen", LineStyle = LineStyle.Solid, Thickness = 1)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "PaleVioletRed", LineStyle = LineStyle.Solid, Thickness = 1)]
        public IndicatorDataSeries DownLine { get; set; }

        private IndicatorDataSeries _sourcePriceDiffDS, _absSourcePriceDiffDS, _tsiDS;
        private MovingAverage _shortMA, _longMA, _signalMA, _smoothedShortMA, _smoothedLongMA, _smoothedSignalMA, _smoothedTriggerMA;

        protected override void Initialize()
        {
            _sourcePriceDiffDS = CreateDataSeries();
            _absSourcePriceDiffDS = CreateDataSeries();
            _tsiDS = CreateDataSeries();

            _shortMA = Indicators.MovingAverage(_sourcePriceDiffDS, ShortPeriod, MAType);
            _longMA = Indicators.MovingAverage(_shortMA.Result, LongPeriod, MAType);
            _signalMA = Indicators.MovingAverage(_longMA.Result, SignalPeriod, MAType);
            _smoothedShortMA = Indicators.MovingAverage(_absSourcePriceDiffDS, ShortPeriod, MAType);
            _smoothedLongMA = Indicators.MovingAverage(_smoothedShortMA.Result, LongPeriod, MAType);
            _smoothedSignalMA = Indicators.MovingAverage(_smoothedLongMA.Result, SignalPeriod, MAType);
            _smoothedTriggerMA = Indicators.MovingAverage(_tsiDS, TriggerPeriod, MAType);
        }

        public override void Calculate(int index)
        {
            _sourcePriceDiffDS[index] = Source[index] - Source[index - 1];
            _absSourcePriceDiffDS[index] = Math.Abs(_sourcePriceDiffDS[index]);
            _tsiDS[index] = Math.Abs(_smoothedSignalMA.Result[index]) < double.Epsilon ? 0 : 100 * _signalMA.Result[index] / _smoothedSignalMA.Result[index];

            UpLine[index] = _tsiDS[index];
            DownLine[index] = _smoothedTriggerMA.Result[index];
        }
    }
}
