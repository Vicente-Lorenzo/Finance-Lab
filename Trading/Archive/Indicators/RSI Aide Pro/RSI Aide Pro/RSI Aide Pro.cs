using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class RSIAidePro : Indicator
    {
        [Parameter("High = Open Color", Group = "Color Settings", DefaultValue = "Blue")]
        public string HighEqualsOpenColor { get; set; }
        [Parameter("High = Close Color", Group = "Color Settings", DefaultValue = "Red")]
        public string HighEqualsCloseColor { get; set; }
        [Parameter("Low = Open Color", Group = "Color Settings", DefaultValue = "Green")]
        public string LowEqualsOpenColor { get; set; }
        [Parameter("Low = Close Color", Group = "Color Settings", DefaultValue = "Gray")]
        public string LowEqualsCloseColor { get; set; }

        [Parameter("Line Extension", Group = "Other Settings", DefaultValue = 20, MinValue = 1)]
        public int LineExtension { get; set; }
        [Parameter("Line Thickness", Group = "Other Settings", DefaultValue = 1, MinValue = 1)]
        public int LineThickness { get; set; }

        private Color _highEqualsOpenColor, _highEqualsCloseColor, _lowEqualsOpenColor, _lowEqualsCloseColor;
        private double _tolerance;

        protected override void Initialize()
        {
            _highEqualsOpenColor = Color.FromName(HighEqualsOpenColor);
            _highEqualsCloseColor = Color.FromName(HighEqualsCloseColor);
            _lowEqualsOpenColor = Color.FromName(LowEqualsOpenColor);
            _lowEqualsCloseColor = Color.FromName(LowEqualsCloseColor);

            _tolerance = Symbol.TickSize;
        }



        public override void Calculate(int index)
        {
            for (var i = 0; i < LineExtension; i++)
                DrawLineProcedure(index - i - 1);
        }

        private void DrawLineProcedure(int index)
        {
            var lineStart = Bars.OpenTimes[index];
            var lineStop = Bars.OpenTimes[index + LineExtension];
            lineStop = lineStop < lineStart ? DateTime.UtcNow : lineStop;

            var open = Bars.OpenPrices[index];
            var high = Bars.HighPrices[index];
            var low = Bars.LowPrices[index];
            var close = Bars.ClosePrices[index];

            if (Math.Abs(high - open) < _tolerance)
                DrawLines(index, lineStart, lineStop, high, _highEqualsOpenColor, "FT");

            if (Math.Abs(high - close) < _tolerance)
                DrawLines(index, lineStart, lineStop, high, _highEqualsCloseColor, "FT");

            if (Math.Abs(low - open) < _tolerance)
                DrawLines(index, lineStart, lineStop, low, _lowEqualsOpenColor, "FB");

            if (Math.Abs(low - close) < _tolerance)
                DrawLines(index, lineStart, lineStop, low, _lowEqualsCloseColor, "FB");
        }

        private void DrawLines(int id, DateTime lineStart, DateTime lineStop, double lineLevel, Color lineColor, string text)
        {
            Chart.DrawTrendLine("Line_" + id + lineColor, lineStart, lineLevel, lineStop, lineLevel, lineColor, LineThickness, LineStyle.Solid);
            Chart.DrawText("Text_" + id + lineColor, text, lineStop, lineLevel, lineColor);
        }
    }
}
