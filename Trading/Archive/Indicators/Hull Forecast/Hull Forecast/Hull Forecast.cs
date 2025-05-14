using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class HullForecast : Indicator
    {
        [Parameter("Source Price")]
        public DataSeries SourcePrice { get; set; }
        [Parameter("Coverage Period", DefaultValue = 35)]
        public int HullCoveragePeriod { get; set; }
        [Parameter("Coverage Period Devisor", DefaultValue = 1.7)]
        public double HullPeriodDivisor { get; set; }

        [Output("Up Line", PlotType = PlotType.Points, LineColor = "White", Thickness = 4)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", PlotType = PlotType.Points, LineColor = "Red", Thickness = 4)]
        public IndicatorDataSeries DownLine { get; set; }

        private HullMovingAverage _ma1;
        private HullMovingAverage _ma2;
        private HullMovingAverage _ma3;

        private IndicatorDataSeries _auxValues;
        private IndicatorDataSeries _auxTrend;

        protected override void Initialize()
        {
            _auxValues = CreateDataSeries();
            _auxTrend = CreateDataSeries();

            _ma1 = Indicators.HullMovingAverage(SourcePrice, (int)Math.Floor(HullCoveragePeriod / HullPeriodDivisor));
            _ma2 = Indicators.HullMovingAverage(SourcePrice, HullCoveragePeriod);
            _ma3 = Indicators.HullMovingAverage(_auxValues, (int)Math.Floor(Math.Sqrt(HullCoveragePeriod)));
        }

        public override void Calculate(int index)
        {
            _auxValues[index] = 2.0 * _ma1.Result[index] - _ma2.Result[index];
            _auxTrend[index] = _auxTrend[index - 1];

            if (_ma3.Result[index] > _ma3.Result[index - 1])
                _auxTrend[index] = 1;
            else if (_ma3.Result[index] < _ma3.Result[index - 1])
                _auxTrend[index] = -1;

            if (_auxTrend[index] > 0)
            {
                UpLine[index] = _ma3.Result[index];
                if (_auxTrend[index - 1] < 0.0)
                    UpLine[index - 1] = _ma3.Result[index - 1];
                DownLine[index] = double.NaN;
            }
            else if (_auxTrend[index] < 0)
            {
                DownLine[index] = _ma3.Result[index];
                if (_auxTrend[index - 1] > 0.0)
                    DownLine[index - 1] = _ma3.Result[index - 1];
                UpLine[index] = double.NaN;
            }
        }
    }
}
