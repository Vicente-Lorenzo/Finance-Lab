using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, ScalePrecision = 4, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomQualitativeQuantitativeEstimation : Indicator
    {
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("RSI Period", DefaultValue = 8, MinValue = 1)]
        public int RsiPeriod { get; set; }
        [Parameter("RSI Smoothing Period", DefaultValue = 1, MinValue = 1)]
        public int RsiSmoothingPeriod { get; set; }
        [Parameter("ATR Period", DefaultValue = 14, MinValue = 1)]
        public int AtrPeriod { get; set; }
        [Parameter("ATR Multiplier", DefaultValue = 3.0, MinValue = 0.1)]
        public double ATRMultiplier { get; set; }
        [Parameter("Moving Average Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "Green", LineStyle = LineStyle.Solid, PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Red", LineStyle = LineStyle.Solid, PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries DownLine { get; set; }

        IndicatorDataSeries _trDS;
        private MovingAverage _qqeMA, _atrMA, _deltaMA;
        private RelativeStrengthIndex _rsi;

        protected override void Initialize()
        {
            _trDS = CreateDataSeries();
            _rsi = Indicators.RelativeStrengthIndex(CloseSource, RsiPeriod);
            _qqeMA = Indicators.MovingAverage(_rsi.Result, RsiSmoothingPeriod, MAType);
            _atrMA = Indicators.MovingAverage(_trDS, AtrPeriod, MAType);
            _deltaMA = Indicators.MovingAverage(_atrMA.Result, RsiPeriod * 2 - 1, MAType);
        }

        public override void Calculate(int index)
        {
            UpLine[index] = _qqeMA.Result[index];
            _trDS[index] = Math.Abs(UpLine[index] - UpLine[index - 1]);
            double downLine = UpLine[index];
            if (UpLine[index] < DownLine[index - 1])
            {
                downLine = UpLine[index] + _deltaMA.Result[index] * ATRMultiplier;
                if (downLine > DownLine[index - 1] && UpLine[index - 1] < DownLine[index - 1])
                {
                    downLine = DownLine[index - 1];
                }
            }
            else if (UpLine[index] > DownLine[index - 1])
            {
                downLine = UpLine[index] - _deltaMA.Result[index] * ATRMultiplier;
                if (downLine < DownLine[index - 1] && UpLine[index - 1] > DownLine[index - 1])
                {
                    downLine = DownLine[index - 1];
                }
            }
            DownLine[index] = downLine;
        }
    }
}
