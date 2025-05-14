using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class ImprovedChaikinMoneyFlow : Indicator
    {
        [Parameter("CMF Period", DefaultValue = 14)]
        public int _cmf_period { get; set; }

        [Parameter("MA Period", DefaultValue = 14)]
        public int _ma_period { get; set; }

        [Parameter("MA Type", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType _ma_type { get; set; }

        [Output("Result 1", LineColor = "Purple")]
        public IndicatorDataSeries Result1 { get; set; }

        [Output("Result 2", LineColor = "Blue")]
        public IndicatorDataSeries Result2 { get; set; }

        private ChaikinMoneyFlow _iCMF;
        private MovingAverage _iMA;

        protected override void Initialize()
        {
            _iCMF = Indicators.ChaikinMoneyFlow(_cmf_period);
            _iMA = Indicators.MovingAverage(Result1, _ma_period, _ma_type);
        }

        public override void Calculate(int index)
        {
            Result1[index] = _iCMF.Result[index];
            Result2[index] = _iMA.Result[index];
        }
    }
}
