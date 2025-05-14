using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, AccessRights = AccessRights.None)]
    public class GannHiLoProIndicator : Indicator
    {
        [Parameter("Period", DefaultValue = 13)]
        public int Period { get; set; }

        [Parameter("Ma Type", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType Matype { get; set; }

        [Parameter("Draw Stairs", DefaultValue = true)]
        public bool UseStairs { get; set; }

        [Output("Up Line", LineColor = "LawnGreen", Thickness = 1, PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries UpSeries { get; set; }

        [Output("Down Line", LineColor = "Red", Thickness = 1, PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries DownSeries { get; set; }

        [Output("Main Line", LineColor = "Yellow", Thickness = 1)]
        public IndicatorDataSeries MainSeries { get; set; }

        private IndicatorDataSeries _auxSeries, _upSeries, _downSeries;
        private MovingAverage _iMaHigh, _iMaLow;

        protected override void Initialize()
        {
            _auxSeries = CreateDataSeries();
            _upSeries = CreateDataSeries();
            _downSeries = CreateDataSeries();
            _iMaHigh = Indicators.MovingAverage(Bars.HighPrices, Period, Matype);
            _iMaLow = Indicators.MovingAverage(Bars.LowPrices, Period, Matype);
        }

        public override void Calculate(int index)
        {
            var close = Bars.ClosePrices[index];
            var highMa = _iMaHigh.Result[index - 1];
            var highPrevMa = _iMaHigh.Result[index - 2];
            var lowMa = _iMaLow.Result[index - 1];

            _upSeries[index] = lowMa;
            _downSeries[index] = highMa;

            if (close > highMa)
            {
                MainSeries[index] = _upSeries[index];
                if (UseStairs)
                {
                    Chart.DrawTrendLine("Up Horizontal" + index, index - 1, _upSeries[index], index, _upSeries[index], Color.SpringGreen);
                    Chart.DrawTrendLine("Up Vertical" + index, index - 1, _upSeries[index - 1], index - 1, _upSeries[index], Color.SpringGreen);
                }
                else
                    UpSeries[index] = _upSeries[index];
            }
            else if (close < lowMa)
            {
                MainSeries[index] = _downSeries[index];
                if (UseStairs)
                {
                    Chart.DrawTrendLine("Down Horizontal" + index, index - 1, _downSeries[index], index, _downSeries[index], Color.Red);
                    Chart.DrawTrendLine("Down Vertical" + index, index - 1, _downSeries[index - 1], index - 1, _downSeries[index], Color.Red);
                }
                else
                    DownSeries[index] = _downSeries[index];
            }
            else if (_auxSeries[index - 1] == highPrevMa)
            {
                MainSeries[index] = _downSeries[index];
                if (UseStairs)
                {
                    Chart.DrawTrendLine("Down Horizontal" + index, index - 1, _downSeries[index], index, _downSeries[index], Color.Red);
                    Chart.DrawTrendLine("Down Vertical" + index, index - 1, _downSeries[index - 1], index - 1, _downSeries[index], Color.Red);
                }
                else
                    DownSeries[index] = _downSeries[index];
            }
            else
            {
                MainSeries[index] = _upSeries[index];
                if (UseStairs)
                {
                    Chart.DrawTrendLine("Up Horizontal" + index, index - 1, _upSeries[index], index, _upSeries[index], Color.SpringGreen);
                    Chart.DrawTrendLine("Up Vertical" + index, index - 1, _upSeries[index - 1], index - 1, _upSeries[index], Color.SpringGreen);
                }
                else
                    UpSeries[index] = _upSeries[index];
            }
        }
    }
}
