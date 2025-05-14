using System;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class PersonalizedIndicator : Indicator
    {
        [Parameter("Source", Group = "Bollinger Band 1 Settings")]
        public DataSeries BB1Source { get; set; }
        [Parameter("Period", Group = "Bollinger Band 1 Settings", DefaultValue = 18)]
        public int BB1Period { get; set; }
        [Parameter("Deviation", Group = "Bollinger Band 1 Settings", DefaultValue = 1.5, Step = 0.1)]
        public double BB1StandardDeviation { get; set; }
        [Parameter("MA Type", Group = "Bollinger Band 1 Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType BB1MaType { get; set; }

        [Parameter("Source", Group = "Bollinger Band 2 Settings")]
        public DataSeries BB2Source { get; set; }
        [Parameter("Period", Group = "Bollinger Band 2 Settings", DefaultValue = 20)]
        public int BB2Period { get; set; }
        [Parameter("Deviation", Group = "Bollinger Band 2 Settings", DefaultValue = 1.5, Step = 0.1)]
        public double BB2StandardDeviation { get; set; }
        [Parameter("MA Type", Group = "Bollinger Band 2 Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType BB2MaType { get; set; }

        [Parameter("Source", Group = "Bollinger Band 3 Settings")]
        public DataSeries BB3Source { get; set; }
        [Parameter("Period", Group = "Bollinger Band 3 Settings", DefaultValue = 25)]
        public int BB3Period { get; set; }
        [Parameter("Deviation", Group = "Bollinger Band 3 Settings", DefaultValue = 1.5, Step = 0.1)]
        public double BB3StandardDeviation { get; set; }
        [Parameter("MA Type", Group = "Bollinger Band 3 Settings", DefaultValue = MovingAverageType.Simple)]
        public MovingAverageType BB3MaType { get; set; }

        [Parameter("Source", Group = "Baseline Settings")]
        public DataSeries BaselineSource { get; set; }
        [Parameter("MA Period", Group = "Baseline Settings", DefaultValue = 200)]
        public int BaselinePeriod { get; set; }
        [Parameter("MA Type", Group = "Baseline Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType BaselineMaType { get; set; }

        [Parameter("Draw Up Arrow", Group = "Arrows Settings", DefaultValue = true)]
        public bool DrawUpArrow { get; set; }
        [Parameter("Draw Down Arrow", Group = "Arrows Settings", DefaultValue = true)]
        public bool DrawDownArrow { get; set; }
        [Parameter("Up Arrow Color", Group = "Arrows Settings", DefaultValue = "RoyalBlue")]
        public string UpArrowColor { get; set; }
        [Parameter("Down Arrow Color", Group = "Arrows Settings", DefaultValue = "IndianRed")]
        public string DownArrowColor { get; set; }
        [Parameter("Up Arrow Distance (Pips)", Group = "Arrows Settings", DefaultValue = 5, Step = 0.1)]
        public double UpArrowDistance { get; set; }
        [Parameter("Down Arrow Distance (Pips)", Group = "Arrows Settings", DefaultValue = 5, Step = 0.1)]
        public double DownArrowDistance { get; set; }

        [Output("BB1 Top", Thickness = 1, LineColor = "Red")]
        public IndicatorDataSeries BB1Top { get; set; }
        [Output("BB2 Top", Thickness = 1, LineColor = "Red")]
        public IndicatorDataSeries BB2Top { get; set; }
        [Output("BB3 Top", Thickness = 1, LineColor = "Red")]
        public IndicatorDataSeries BB3Top { get; set; }

        [Output("BB1 Main", Thickness = 1, LineColor = "Gray")]
        public IndicatorDataSeries BB1Main { get; set; }
        [Output("BB2 Main", Thickness = 1, LineColor = "Gray")]
        public IndicatorDataSeries BB2Main { get; set; }
        [Output("BB3 Main", Thickness = 1, LineColor = "Gray")]
        public IndicatorDataSeries BB3Main { get; set; }

        [Output("BB1 Bottom", Thickness = 1, LineColor = "Green")]
        public IndicatorDataSeries BB1Bottom { get; set; }
        [Output("BB2 Bottom", Thickness = 1, LineColor = "Green")]
        public IndicatorDataSeries BB2Bottom { get; set; }
        [Output("BB3 Bottom", Thickness = 1, LineColor = "Green")]
        public IndicatorDataSeries BB3Bottom { get; set; }

        [Output("Baseline Rising", Thickness = 2, LineColor = "RoyalBlue", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries BaselineRising { get; set; }
        [Output("Baseline Stable", Thickness = 2, LineColor = "Gray", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries BaselineStable { get; set; }
        [Output("Baseline Falling", Thickness = 2, LineColor = "IndianRed", PlotType = PlotType.DiscontinuousLine)]
        public IndicatorDataSeries BaselineFalling { get; set; }

        private BollingerBands _iBB1, _iBB2, _iBB3;
        private MovingAverage _iBaseline;
        private Color _upArrowColor, _downArrowColor;

        protected override void Initialize()
        {
            _iBB1 = Indicators.BollingerBands(BB1Source, BB1Period, BB1StandardDeviation, BB1MaType);
            _iBB2 = Indicators.BollingerBands(BB2Source, BB2Period, BB2StandardDeviation, BB2MaType);
            _iBB3 = Indicators.BollingerBands(BB3Source, BB3Period, BB3StandardDeviation, BB3MaType);

            _iBaseline = Indicators.MovingAverage(BaselineSource, BaselinePeriod, BaselineMaType);

            _upArrowColor = Color.FromName(UpArrowColor);
            _downArrowColor = Color.FromName(DownArrowColor);
        }

        public override void Calculate(int index)
        {
            BB1Top[index] = _iBB1.Top[index];
            BB1Main[index] = _iBB1.Main[index];
            BB1Bottom[index] = _iBB1.Bottom[index];

            BB2Top[index] = _iBB2.Top[index];
            BB2Main[index] = _iBB2.Main[index];
            BB2Bottom[index] = _iBB2.Bottom[index];

            BB3Top[index] = _iBB3.Top[index];
            BB3Main[index] = _iBB3.Main[index];
            BB3Bottom[index] = _iBB3.Bottom[index];

            if (_iBaseline.Result[index] > _iBaseline.Result[index - 1])
            {
                BaselineRising[index - 1] = _iBaseline.Result[index - 1];
                BaselineRising[index] = _iBaseline.Result[index];
            }
            else if (_iBaseline.Result[index] < _iBaseline.Result[index - 1])
            {
                BaselineFalling[index - 1] = _iBaseline.Result[index - 1];
                BaselineFalling[index] = _iBaseline.Result[index];
            }
            else
            {
                BaselineStable[index - 1] = _iBaseline.Result[index - 1];
                BaselineStable[index] = _iBaseline.Result[index];
            }

            var open = Bars.OpenPrices[index];
            var high = Bars.HighPrices[index];
            var low = Bars.LowPrices[index];
            var close = Bars.ClosePrices[index];
            var open1 = Bars.OpenPrices[index - 1];
            var open2 = Bars.OpenPrices[index - 2];
            var close1 = Bars.ClosePrices[index - 1];
            var close2 = Bars.ClosePrices[index - 2];
            var high1 = Bars.HighPrices[index - 1];
            var high2 = Bars.HighPrices[index - 2];
            var low1 = Bars.LowPrices[index - 1];

            if (close2 < open2 && Math.Max(open1, close1) < close2 && open > Math.Max(open1, close1) && close > open)
                ChartDrawUpArrow(index);
            if (open1 > close1 && close > open && close <= open1 && close1 <= open && close - open < open1 - close1)
                ChartDrawUpArrow(index);
            if (open1 > close1 && close > open && close >= open1 && close1 >= open && close - open > open1 - close1)
                ChartDrawUpArrow(index);
            if (close1 < open1 && open < low1 && close > close1 + ((open1 - close1) / 2) && close < open1)
                ChartDrawUpArrow(index);
            if (low == open && open < Bars.LowPrices.Minimum(10) && open < close && close > ((high1 - low1) / 2) + low1)
                ChartDrawUpArrow(index);
            if (open1 > close1 && open >= open1 && close > open)
                ChartDrawUpArrow(index);

            if (close2 > open2 && Math.Min(open1, close1) > close2 && open < Math.Min(open1, close1) && close < open)
                ChartDrawDownArrow(index);
            if (open1 < close1 && open > close1 && high - Math.Max(open, close) >= Math.Abs(open - close) * 3 && Math.Min(close, open) - low <= Math.Abs(open - close))
                ChartDrawDownArrow(index);
            if (close1 > open1 && open > close && open <= close1 && open1 <= close && open - close < close1 - open1)
                ChartDrawDownArrow(index);
            if (close1 > open1 && open > close && open >= close1 && open1 >= close && open - close > close1 - open1)
                ChartDrawDownArrow(index);
            if (open1 < close1 && open <= open1 && close <= open)
                ChartDrawDownArrow(index);
            if (((high - low > 4 * (open - close)) && ((close - low) / (0.001 + high - low) >= 0.75) && ((open - low) / (0.001 + high - low) >= 0.75)) && high1 < open && high2 < open)
                ChartDrawDownArrow(index);
            if ((close1 > open1) && (((close1 + open1) / 2) > close) && (open > close) && (open > close1) && (close > open1) && ((open - close) / (0.001 + (high - low)) > 0.6))
                ChartDrawDownArrow(index);
        }

        private void ChartDrawUpArrow(int index)
        {
            if (!DrawUpArrow)
                return;
            Chart.DrawIcon("UpArrow_" + index, ChartIconType.UpArrow, Bars.OpenTimes[index], Bars.LowPrices[index] - UpArrowDistance * Symbol.PipSize, _upArrowColor);
            Chart.DrawText("UpArrowText_" + index, "Call", Bars.OpenTimes[index], Bars.LowPrices[index] - (UpArrowDistance) * Symbol.PipSize, _upArrowColor);
        }

        private void ChartDrawDownArrow(int index)
        {
            if (!DrawDownArrow)
                return;
            Chart.DrawIcon("DownArrow_" + index, ChartIconType.DownArrow, Bars.OpenTimes[index], Bars.HighPrices[index] + DownArrowDistance * Symbol.PipSize, _downArrowColor);
            Chart.DrawText("DownArrowText_" + index, "Put", Bars.OpenTimes[index], Bars.HighPrices[index] + (DownArrowDistance) * Symbol.PipSize, _downArrowColor);
        }
    }
}
