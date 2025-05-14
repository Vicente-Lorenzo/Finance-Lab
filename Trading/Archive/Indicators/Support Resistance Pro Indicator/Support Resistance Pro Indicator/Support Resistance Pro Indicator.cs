using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class SupportResistanceProIndicator : Indicator
    {
        [Parameter("Lines To Show", Group = "Resistance Lines Settings", DefaultValue = 3)]
        public int ResistancesToShow { get; set; }
        [Parameter("Line Width", Group = "Resistance Lines Settings", DefaultValue = 4, MinValue = 1)]
        public int ResistancesWidth { get; set; }
        [Parameter("Line Color", Group = "Resistance Lines Settings", DefaultValue = "Orange")]
        public string ResistancesColor { get; set; }

        [Parameter("Lines To Show", Group = "Support Lines Settings", DefaultValue = 3)]
        public int SupportsToShow { get; set; }
        [Parameter("Line Width", Group = "Support Lines Settings", DefaultValue = 4, MinValue = 1)]
        public int SupportsWidth { get; set; }
        [Parameter("Line Color", Group = "Support Lines Settings", DefaultValue = "Orange")]
        public string SupportsColor { get; set; }

        [Output("Resistance Line", LineColor = "Purple", Thickness = 1)]
        public IndicatorDataSeries ResistanceLine { get; set; }
        [Output("Support Line", LineColor = "Yellow", Thickness = 1)]
        public IndicatorDataSeries SupportLine { get; set; }

        private Color _supportsColor, _resistancesColor;
        private MovingAverage _iHmaSrc1, _iHmaSrc2;
        private IndicatorDataSeries _hmaChangeSrc1, _hmaChangeSrc2, _highest, _lowest, _resistance, _resistanceValues, _resistanceIndex, _support, _supportValues, _supportIndex;
        private StandardDeviation _iHighDeviation, _iLowDeviation;
        private RelativeStrengthIndex _iRsi;
        private double _lastHPivot = double.NaN, _lastLPivot = double.NaN, _lastXup = double.NaN, _lastXdown = double.NaN;

        protected override void Initialize()
        {
            _supportsColor = Color.FromName(SupportsColor);
            _resistancesColor = Color.FromName(ResistancesColor);

            _iHmaSrc1 = Indicators.MovingAverage(Bars.OpenPrices, 5, MovingAverageType.Hull);
            _iHmaSrc2 = Indicators.MovingAverage(Bars.ClosePrices, 12, MovingAverageType.Hull);
            _hmaChangeSrc1 = CreateDataSeries();
            _hmaChangeSrc2 = CreateDataSeries();

            _highest = CreateDataSeries();
            _lowest = CreateDataSeries();
            _iHighDeviation = Indicators.StandardDeviation(_highest, 2, MovingAverageType.Simple);
            _iLowDeviation = Indicators.StandardDeviation(_lowest, 2, MovingAverageType.Simple);

            _iRsi = Indicators.RelativeStrengthIndex(Bars.ClosePrices, 9);

            _resistance = CreateDataSeries();
            _resistanceValues = CreateDataSeries();
            _resistanceIndex = CreateDataSeries();
            _support = CreateDataSeries();
            _supportValues = CreateDataSeries();
            _supportIndex = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            UpdateHmaChangeSrc1(index);
            UpdateHmaChangeSrc2(index);
            var momm1 = _hmaChangeSrc1[index];
            var momm2 = _hmaChangeSrc2[index];
            var sm1 = f1(momm1, momm2);
            var sm2 = f2(momm1, momm2);
            var cmoNew = percent(sm1 - sm2, sm1 + sm2);

            UpdateHighest(index);
            UpdateLowest(index);
            var hPivot = FixNaN(_iHighDeviation.Result[index] > Symbol.PointSize ? double.NaN : _highest[index], ref _lastHPivot);
            var lPivot = FixNaN(_iLowDeviation.Result[index] > Symbol.PointSize ? double.NaN : _lowest[index], ref _lastLPivot);

            var rsiNew = _iRsi.Result[index];
            var sup = rsiNew < 25 && cmoNew > 50 && !double.IsNaN(lPivot) && lPivot > Symbol.PointSize;
            var res = rsiNew > 75 && cmoNew < -50 && !double.IsNaN(hPivot) && hPivot > Symbol.PointSize;
            UpdateResistance(index, res);
            UpdateSupport(index, sup);

            ResistanceLine[index] = _resistance[index];
            SupportLine[index] = _support[index];

            if (!IsLastBar)
                return;

            for (var i = ResistancesToShow - 1; i > -1; i--)
            {
                var startTime = CalculateStartDate(i, _resistanceIndex);
                var stopTime = CalculateStopDate(i, _resistanceIndex);
                DrawResistanceLine(i, startTime, stopTime, _resistanceValues.Last(i), _resistancesColor, ResistancesWidth);
            }

            for (var i = SupportsToShow - 1; i > -1; i--)
            {
                var startTime = CalculateStartDate(i, _supportIndex);
                var stopTime = CalculateStopDate(i, _supportIndex);
                DrawSupportLine(i, startTime, stopTime, _supportValues.Last(i), _supportsColor, SupportsWidth);
            }
        }

        private DateTime CalculateStartDate(int lastIndex, IndicatorDataSeries indexes)
        {
            return Bars.OpenTimes[(int)indexes.Last(lastIndex)];
        }

        private DateTime CalculateStopDate(int lastIndex, IndicatorDataSeries indexes)
        {
            return lastIndex - 1 < 0 ? DateTime.UtcNow : Bars.OpenTimes[(int)indexes.Last(lastIndex - 1)];
        }

        private void DrawSupportLine(int id, DateTime lineStart, DateTime lineEnd, double highLevel, Color highLineColor, int lineThickness)
        {
            Chart.DrawTrendLine("SupportLine_" + id, lineStart, highLevel, lineEnd, highLevel, highLineColor, lineThickness, LineStyle.Solid);
        }

        private void DrawResistanceLine(int id, DateTime lineStart, DateTime lineEnd, double highLevel, Color highLineColor, int lineThickness)
        {
            Chart.DrawTrendLine("ResistanceLine_" + id, lineStart, highLevel, lineEnd, highLevel, highLineColor, lineThickness, LineStyle.Solid);
        }

        private double f1(double m, double n)
        {
            return m >= n ? m : 0.0;
        }

        private double f2(double m, double n)
        {
            return m >= n ? 0.0 : -m;
        }

        private void UpdateHmaChangeSrc1(int index)
        {
            _hmaChangeSrc1[index] = _iHmaSrc1.Result[index - 1] - _iHmaSrc1.Result[index - 2];
        }

        private void UpdateHmaChangeSrc2(int index)
        {
            _hmaChangeSrc2[index] = _iHmaSrc2.Result[index] - _iHmaSrc2.Result[index - 1];
        }

        private double percent(double nom, double div)
        {
            return 100 * nom / div;
        }

        private void UpdateHighest(int index)
        {
            _highest[index] = Math.Max(Bars.HighPrices[index], Bars.HighPrices[index - 1]);
        }

        private void UpdateLowest(int index)
        {
            _lowest[index] = Math.Min(Bars.LowPrices[index], Bars.LowPrices[index - 1]);
        }

        private void UpdateResistance(int index, bool sup)
        {
            _resistance[index] = FixNaN(sup ? Bars.HighPrices[index] : _resistance[1], ref _lastXup);
            if (Math.Abs(_resistance[index] - _resistance[index - 1]) > Symbol.PointSize)
            {
                _resistanceValues[_resistanceValues.Count] = _resistance[index];
                _resistanceIndex[_resistanceIndex.Count] = index;
            }
        }

        private void UpdateSupport(int index, bool res)
        {
            _support[index] = FixNaN(res ? Bars.LowPrices[index] : _support[1], ref _lastXdown);
            if (Math.Abs(_support[index] - _support[index - 1]) > Symbol.PointSize)
            {
                _supportValues[_supportValues.Count] = _support[index];
                _supportIndex[_supportIndex.Count] = index;
            }
        }

        private double FixNaN(double newValue, ref double lastNonNaNvalue)
        {
            if (double.IsNaN(lastNonNaNvalue))
                lastNonNaNvalue = newValue;
            else if (double.IsNaN(newValue))
                newValue = lastNonNaNvalue;
            else
                lastNonNaNvalue = newValue;
            return newValue;
        }
    }
}
