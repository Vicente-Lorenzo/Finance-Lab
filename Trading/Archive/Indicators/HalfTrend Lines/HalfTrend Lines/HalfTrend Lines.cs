using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class HalfTrendLines : Indicator
    {
        [Parameter("Amplitude", DefaultValue = 2)]
        public int Amplitude { get; set; }
        [Output("Up Line", LineColor = "SkyBlue", Thickness = 2)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Tomato", Thickness = 2)]
        public IndicatorDataSeries DownLine { get; set; }

        private bool _nextTrend = false;
        private double _minHighPrice, _maxLowPrice;
        private IndicatorDataSeries _trend;
        private SimpleMovingAverage _lowMa, _highMa;

        protected override void Initialize()
        {
            _trend = CreateDataSeries();

            _lowMa = Indicators.SimpleMovingAverage(Bars.LowPrices, Amplitude);
            _highMa = Indicators.SimpleMovingAverage(Bars.HighPrices, Amplitude);

            _minHighPrice = Bars.HighPrices.LastValue;
            _maxLowPrice = Bars.LowPrices.LastValue;
        }

        public override void Calculate(int index)
        {
            var lowPrice = double.PositiveInfinity;
            var highPrice = double.NegativeInfinity;
            for (var i = 0; i < Amplitude; i++)
            {
                lowPrice = Math.Min(lowPrice, Bars.LowPrices[index - i]);
                highPrice = Math.Max(highPrice, Bars.HighPrices[index - i]);
            }
            var lowMa = _lowMa.Result[index];
            var highMa = _highMa.Result[index];
            _trend[index] = _trend[index - 1];
            if (_nextTrend)
            {
                if (!double.IsNaN(lowPrice))
                    _maxLowPrice = Math.Max(_maxLowPrice, lowPrice);
                if (highMa < _maxLowPrice && Bars.ClosePrices[index] < Bars.LowPrices[index - 1])
                {
                    _trend[index] = 1.0;
                    _nextTrend = false;
                    _minHighPrice = highPrice;
                }
            }

            if (!_nextTrend)
            {
                if (!double.IsNaN(highPrice))
                    _minHighPrice = Math.Min(_minHighPrice, highPrice);
                if (lowMa > _minHighPrice && Bars.ClosePrices[index] > Bars.HighPrices[index - 1])
                {
                    _trend[index] = 0.0;
                    _nextTrend = true;
                    _maxLowPrice = lowPrice;
                }
            }

            if (_trend[index] == 0.0)
            {
                if (_trend[index - 1] != 0.0)
                {
                    UpLine[index] = DownLine[index - 1];
                    UpLine[index - 1] = UpLine[index];
                }
                else
                {
                    if (!double.IsNaN(UpLine[index - 1]))
                        UpLine[index] = Math.Max(_maxLowPrice, UpLine[index - 1]);
                    else
                        UpLine[index] = _maxLowPrice;
                }
                DownLine[index] = UpLine[index] - 0.005;
            }
            else
            {
                if (_trend[index - 1] != 1.0)
                {
                    DownLine[index] = UpLine[index - 1];
                    DownLine[index - 1] = DownLine[index];
                }
                else
                {
                    if (!double.IsNaN(DownLine[index - 1]))
                        DownLine[index] = Math.Min(_minHighPrice, DownLine[index - 1]);
                    else
                        DownLine[index] = _minHighPrice;
                }
                UpLine[index] = DownLine[index] - 0.005;
            }
        }
    }
}
