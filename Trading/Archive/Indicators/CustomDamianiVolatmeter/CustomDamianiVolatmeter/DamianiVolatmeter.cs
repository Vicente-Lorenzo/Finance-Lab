using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class CustomDamianiVolatmeter : Indicator
    {
        [Parameter("HighSource")]
        public DataSeries HighSource { get; set; }
        [Parameter("LowSource")]
        public DataSeries LowSource { get; set; }
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("TypicalSource")]
        public DataSeries TypicalSource { get; set; }
        [Parameter("Viscosity", DefaultValue = 7, MinValue = 1)]
        public int Viscosity { get; set; }
        [Parameter("Sedimentation", DefaultValue = 50, MinValue = 1)]
        public int Sedimentation { get; set; }
        [Parameter("Threshold", DefaultValue = 1.1, MinValue = 1.0)]
        public double Threshold { get; set; }
        [Parameter("Lag Supressor", DefaultValue = true)]
        public bool LagSupresssor { get; set; }
        [Parameter("Lag Multiplier", DefaultValue = 0.5, MinValue = 0.1)]
        public double LagMultiplier { get; set; }
        [Parameter("ATR MA Type", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType ATRMAType { get; set; }
        [Parameter("SD MA Type", DefaultValue = MovingAverageType.Weighted)]
        public MovingAverageType SDMAType { get; set; }
        [Output("Bad Volume", LineColor = "Silver")]
        public IndicatorDataSeries BadVolumeLine { get; set; }
        [Output("Opportunities", LineColor = "Red")]
        public IndicatorDataSeries OpportunitiesLine { get; set; }
        [Output("Good Volume", LineColor = "Lime")]
        public IndicatorDataSeries GoodVolumeLine { get; set; }

        private IndicatorDataSeries _tempVolume;
        private CustomAverageTrueRange _iATRViscosity, _iATRSedimentation;
        private StandardDeviation _iSTDViscosity, _iSTDSedimentation;

        protected override void Initialize()
        {
            _tempVolume = CreateDataSeries();
            _iATRViscosity = Indicators.GetIndicator<CustomAverageTrueRange>(HighSource, LowSource, CloseSource, Viscosity, ATRMAType);
            _iATRSedimentation = Indicators.GetIndicator<CustomAverageTrueRange>(HighSource, LowSource, CloseSource, Sedimentation, ATRMAType);
            _iSTDViscosity = Indicators.StandardDeviation(TypicalSource, Viscosity, SDMAType);
            _iSTDSedimentation = Indicators.StandardDeviation(TypicalSource, Sedimentation, SDMAType);
        }

        public override void Calculate(int index)
        {
            double sa = _iATRViscosity.Result[index];
            double s1 = _tempVolume[index - 1];
            double s3 = _tempVolume[index - 3];
            double vol;
            if (LagSupresssor)
            {
                double val = (double.IsNaN(s1 - s3)) ? 0 : s1 - s3;
                vol = sa / _iATRSedimentation.Result[index] + LagMultiplier * val;
            }
            else
                vol = sa / _iATRSedimentation.Result[index];
            double anti_thres = _iSTDViscosity.Result[index];
            anti_thres = anti_thres / _iSTDSedimentation.Result[index];
            double t = Threshold;
            t = t - anti_thres;
            if (vol > t)
            {
                GoodVolumeLine[index] = vol;
                OpportunitiesLine[index] = vol;
            }
            else
            {
                GoodVolumeLine[index] = vol;
                OpportunitiesLine[index] = double.NaN;
            }
            _tempVolume[index] = vol;
            BadVolumeLine[index] = t;
        }
    }
}
