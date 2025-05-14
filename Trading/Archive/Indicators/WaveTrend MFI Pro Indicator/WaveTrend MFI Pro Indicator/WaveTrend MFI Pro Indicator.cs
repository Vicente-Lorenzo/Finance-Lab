using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Cloud("Long WaveTrend", "Short WaveTrend", FirstColor = "RoyalBlue", SecondColor = "RoyalBlue")]
    [Cloud("Long WaveTrend", "Zero Line", FirstColor = "RoyalBlue", SecondColor = "RoyalBlue")]
    [Cloud("Short WaveTrend", "Zero Line", FirstColor = "IndianRed", SecondColor = "IndianRed")]

    [Cloud("Long WaveTrend", "Short WaveTrend", FirstColor = "RoyalBlue", SecondColor = "RoyalBlue")]
    [Cloud("Long WaveTrend", "Zero Line", FirstColor = "RoyalBlue", SecondColor = "RoyalBlue")]
    [Cloud("Short WaveTrend", "Zero Line", FirstColor = "IndianRed", SecondColor = "IndianRed")]

    [Cloud("MFI", "Zero Line", FirstColor = "LimeGreen", SecondColor = "Red")]
    [Cloud("MFI", "Zero Line", FirstColor = "LimeGreen", SecondColor = "Red")]

    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class WaveTrendMFIProIndicator : Indicator
    {
        [Parameter("Channel Period", Group = "WaveTrend Settings", DefaultValue = 9, MinValue = 1)]
        public int WtChannelPeriod { get; set; }
        [Parameter("Average Period", Group = "WaveTrend Settings", DefaultValue = 12, MinValue = 1)]
        public int WtAveragePeriod { get; set; }
        [Parameter("MA Period", Group = "WaveTrend Settings", DefaultValue = 3, MinValue = 1)]
        public int WtMaPeriod { get; set; }

        [Parameter("Source", Group = "RSI Settings")]
        public DataSeries RsiSource { get; set; }
        [Parameter("Period", Group = "RSI Settings", DefaultValue = 14)]
        public int RsiPeriod { get; set; }

        [Parameter("Period", Group = "MFI Settings", DefaultValue = 60)]
        public int MfiPeriod { get; set; }
        [Parameter("Multiplier", Group = "MFI Settings", DefaultValue = 150)]
        public int MfiMultiplier { get; set; }

        [Output("Long WaveTrend", LineColor = "Transparent")]
        public IndicatorDataSeries LongWaveTrend { get; set; }
        [Output("Short WaveTrend", LineColor = "Transparent")]
        public IndicatorDataSeries ShortWaveTrend { get; set; }

        [Output("MFI", LineColor = "Transparent")]
        public IndicatorDataSeries Mfi { get; set; }

        [Output("Zero Line", LineColor = "Transparent")]
        public IndicatorDataSeries ZeroLine { get; set; }

        private MovingAverage _esa, _de, _iWt1, _iWt2, _iMfi;
        private IndicatorDataSeries _aux0, _aux1, _aux2, _aux3;
        private RelativeStrengthIndex _iRsi;

        protected override void Initialize()
        {
            _aux0 = CreateDataSeries();
            _esa = Indicators.MovingAverage(_aux0, WtChannelPeriod, MovingAverageType.Exponential);
            _aux1 = CreateDataSeries();
            _de = Indicators.MovingAverage(_aux1, WtChannelPeriod, MovingAverageType.Exponential);
            _aux2 = CreateDataSeries();
            _iWt1 = Indicators.MovingAverage(_aux2, WtAveragePeriod, MovingAverageType.Exponential);
            _iWt2 = Indicators.MovingAverage(_iWt1.Result, WtMaPeriod, MovingAverageType.Simple);
            _iRsi = Indicators.RelativeStrengthIndex(RsiSource, RsiPeriod);
            _aux3 = CreateDataSeries();
            _iMfi = Indicators.MovingAverage(_aux3, MfiPeriod, MovingAverageType.Simple);
        }

        public override void Calculate(int index)
        {
            _aux0[index] = (Bars.HighPrices[index] + Bars.LowPrices[index] + Bars.ClosePrices[index]) / 3;
            _aux1[index] = Math.Abs(_aux0[index] - _esa.Result[index]);
            _aux2[index] = (_aux0[index] - _esa.Result[index]) / (0.015 * _de.Result[index]);
            _aux3[index] = (Bars.ClosePrices[index] - Bars.OpenPrices[index]) / (Bars.HighPrices[index] - Bars.LowPrices[index]) * MfiMultiplier;

            LongWaveTrend[index] = _iWt1.Result[index];
            ShortWaveTrend[index] = _iWt2.Result[index];
            ZeroLine[index] = 0.0;

            Mfi[index] = _iMfi.Result[index];
        }
    }
}
