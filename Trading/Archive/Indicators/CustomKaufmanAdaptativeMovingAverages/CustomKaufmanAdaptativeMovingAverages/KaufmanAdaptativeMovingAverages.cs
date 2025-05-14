using System;
using cAlgo.API;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, AccessRights = AccessRights.None)]
    public class CustomKaufmanAdaptativeMovingAverages : Indicator
    {
        [Parameter("CloseSource")]
        public DataSeries CloseSource { get; set; }
        [Parameter("Short Period", DefaultValue = 2, MinValue = 1)]
        public int ShortPeriod { get; set; }
        [Parameter("Long Period", DefaultValue = 30, MinValue = 1)]
        public int LongPeriod { get; set; }
        [Parameter("Signal Period", DefaultValue = 10, MinValue = 1)]
        public int SignalPeriod { get; set; }
        [Output("Baseline", LineColor = "Violet")]
        public IndicatorDataSeries Result { get; set; }

        private IndicatorDataSeries _sourceDiffDS;

        protected override void Initialize()
        {
            _sourceDiffDS = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            _sourceDiffDS[index] = Math.Abs(CloseSource[index] - CloseSource[index - 1]);
            if (index < SignalPeriod)
            {
                Result[index] = CloseSource[index];
                return;
            }

            double shortd = 2.0 / (double)(ShortPeriod + 1);
            double longd = 2.0 / (double)(LongPeriod + 1);
            double signal = Math.Abs(CloseSource[index] - CloseSource[index - SignalPeriod]);
            double noise = 0;
            for (int i = 0; i < SignalPeriod; i++)
            {
                noise += _sourceDiffDS[index - i];
            }
            if (noise == 0)
            {
                Result[index] = Result[index - 1];
                return;
            }
            double smooth = Math.Pow((signal / noise) * (shortd - longd) + longd, 2);
            Result[index] = Result[index - 1] + smooth * (CloseSource[index] - Result[index - 1]);
        }
    }
}
