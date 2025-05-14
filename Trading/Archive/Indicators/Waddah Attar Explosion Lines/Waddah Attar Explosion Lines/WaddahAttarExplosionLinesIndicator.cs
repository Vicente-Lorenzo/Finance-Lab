using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class WaddahAttarExplosionLines : Indicator
    {
        [Parameter("Sensibility", DefaultValue = 90, MinValue = 1)]
        public int _sensibility { get; set; }

        [Parameter("MACD Long Period", DefaultValue = 26, MinValue = 1)]
        public int _macd_first_period { get; set; }

        [Parameter("MACD Short Period", DefaultValue = 12, MinValue = 1)]
        public int _macd_second_period { get; set; }

        [Parameter("MACD Signal Period", DefaultValue = 9, MinValue = 1)]
        public int _macd_signal_period { get; set; }

        [Parameter("MACD MA", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType _macd_ma_type { get; set; }

        [Parameter("BB Period", DefaultValue = 20, MinValue = 1)]
        public int _bb_period { get; set; }

        [Parameter("BB Standard Deviation", DefaultValue = 2.5, MinValue = 0.1)]
        public double _bb_sd { get; set; }

        [Parameter("BB MA", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType _bb_ma_type { get; set; }

        [Output("Result 1", LineColor = "Yellow", Thickness = 1)]
        public IndicatorDataSeries Result1 { get; set; }

        [Output("Result 2", LineColor = "Red", Thickness = 1)]
        public IndicatorDataSeries Result2 { get; set; }

        private ZeroLagMACDIndicator _iMACD;
        private BollingerBands _iBBands;

        protected override void Initialize()
        {
            _iMACD = Indicators.GetIndicator<ZeroLagMACDIndicator>(_macd_first_period, _macd_second_period, _macd_signal_period, _macd_ma_type);
            _iBBands = Indicators.BollingerBands(Bars.ClosePrices, _bb_period, _bb_sd, _bb_ma_type);
        }

        public override void Calculate(int index)
        {
            Result1[index] = Math.Abs((_iMACD.Result1[index] - _iMACD.Result1[index - 1]) * _sensibility);
            Result2[index] = (_iBBands.Top[index] - _iBBands.Bottom[index]);
        }
    }
}
