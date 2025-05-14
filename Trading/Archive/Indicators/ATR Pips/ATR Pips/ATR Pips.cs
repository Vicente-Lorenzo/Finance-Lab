using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class ATRPips : Indicator
    {
        [Parameter("TimeFrame", Group = "ATR Settings", DefaultValue = "Daily")]
        public TimeFrame ATRTimeFrame { get; set; }
        [Parameter("Period", Group = "ATR Settings", DefaultValue = 15, MinValue = 1)]
        public int ATRPeriod { get; set; }
        [Parameter("MA Type", Group = "ATR Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType ATRMaType { get; set; }

        [Output("ATR Pips", LineColor = "Yellow")]
        public IndicatorDataSeries Result { get; set; }

        private Bars _atrBars;
        private AverageTrueRange _iATR;

        protected override void Initialize()
        {
            _atrBars = MarketData.GetBars(ATRTimeFrame);
            _iATR = Indicators.AverageTrueRange(_atrBars, ATRPeriod, ATRMaType);
        }

        public override void Calculate(int index)
        {
            Result[index] = _iATR.Result[_atrBars.OpenTimes.GetIndexByTime(Bars.OpenTimes[index])] / Symbol.PipSize;

        }
    }
}
