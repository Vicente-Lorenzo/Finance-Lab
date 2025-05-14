using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomSSL : Indicator
    {
        [Parameter("HighSource")]
        public DataSeries HighSource { get; set; }
        [Parameter("LowSource")]
        public DataSeries LowSource { get; set; }
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("Period", DefaultValue = 10, MinValue = 1)]
        public int Period { get; set; }
        [Parameter("MA Type", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType MAType { get; set; }
        [Output("Up Line", LineColor = "Green")]
        public IndicatorDataSeries UpLine { get; set; }
        [Output("Down Line", LineColor = "Red")]
        public IndicatorDataSeries DownLine { get; set; }

        private MovingAverage _highMA, _lowMA;
        private IndicatorDataSeries _tempDS;

        protected override void Initialize()
        {
            _highMA = Indicators.MovingAverage(HighSource, Period, MAType);
            _lowMA = Indicators.MovingAverage(LowSource, Period, MAType);
            _tempDS = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            _tempDS[index] = CloseSource[index] > _highMA.Result[index] ? 1 : CloseSource[index] < _lowMA.Result[index] ? -1 : _tempDS[index - 1];
            UpLine[index] = _tempDS[index] < 0 ? _lowMA.Result[index] : _highMA.Result[index];
            DownLine[index] = _tempDS[index] < 0 ? _highMA.Result[index] : _lowMA.Result[index];
        }
    }
}
