using System;
using System.Net;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class BTMMWorkTime : Indicator
    {
        [Parameter("Ma Period", Group = "Signal Moving Average Settings", DefaultValue = 5)]
        public int SignalMaPeriod { get; set; }
        [Parameter("Ma Type", Group = "Signal Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SignaltMaType { get; set; }

        [Parameter("Ma Period", Group = "Baseline Moving Average Settings", DefaultValue = 13)]
        public int BaselineMaPeriod { get; set; }
        [Parameter("Ma Type", Group = "Baseline Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType BaselineMaType { get; set; }

        [Parameter("Ma Period", Group = "Short Moving Average Settings", DefaultValue = 50)]
        public int ShortMaPeriod { get; set; }
        [Parameter("Ma Type", Group = "Short Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType ShortMaType { get; set; }

        [Parameter("Ma Period", Group = "Long Moving Average Settings", DefaultValue = 200)]
        public int LongMaPeriod { get; set; }
        [Parameter("Ma Type", Group = "Long Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType LongMaType { get; set; }

        [Parameter("Boxes Opacity", Group = "Asia Box", DefaultValue = 20)]
        public int BoxOpt { get; set; }
        [Parameter("Asia Color", Group = "Asia Box", DefaultValue = "Cyan")]
        public string AsiaColor { get; set; }

        [Parameter("Asia Zones Distance", Group = "Asia Areas", DefaultValue = 25)]
        public double AsiaZoneDist { get; set; }
        [Parameter("Asia Zones Width", Group = "Asia Areas", DefaultValue = 25)]
        public double AsiaZoneWidth { get; set; }

        [Parameter("Stop Hunt Width (-1 to deactivate)", Group = "Asia Areas", DefaultValue = 50)]
        public int StopHuntPips { get; set; }

        [Parameter("Asia Levels Thickess", Group = "Asia Levels", DefaultValue = 1)]
        public int AsiaLevelsThc { get; set; }
        [Parameter("Asia Levels LineStyle", Group = "Asia Levels", DefaultValue = LineStyle.Lines)]
        public LineStyle AsiaLevelsLS { get; set; }
        [Parameter("Asia Levels Opacity", Group = "Asia Levels", DefaultValue = 25)]
        public int AsiaLevelsOpt { get; set; }
        [Parameter("Asia Levels Color", Group = "Asia Levels", DefaultValue = "Yellow")]
        public string AsiaLevelsColor { get; set; }

        [Parameter("Brinks Color", Group = "Brinks Box", DefaultValue = "LimeGreen")]
        public string BrinksColor { get; set; }
        [Parameter("Brinks Opacity", Group = "Brinks Box", DefaultValue = 25)]
        public int BrinksOpt { get; set; }

        [Parameter("Brinks 2 Color", Group = "Brinks Box 2", DefaultValue = "Yellow")]
        public string Brinks2Color { get; set; }
        [Parameter("Brinks 2 Opacity", Group = "Brinks Box 2", DefaultValue = 25)]
        public int Brinks2Opt { get; set; }

        [Parameter("US Color", Group = "US Box", DefaultValue = "Red")]
        public string USColor { get; set; }
        [Parameter("US Opacity", Group = "US Box ", DefaultValue = 25)]
        public int USOpt { get; set; }

        [Parameter("Daily Range Color", Group = "Daily Range", DefaultValue = "SkyBlue")]
        public string DailyColor { get; set; }
        [Parameter("Daily Range Thickess", Group = "Daily Range", DefaultValue = 1)]
        public int DailyThc { get; set; }
        [Parameter("Daily Range LineStyle", Group = "Daily Range", DefaultValue = LineStyle.LinesDots)]
        public LineStyle DailyLS { get; set; }
        [Parameter("ADR Color", Group = "ADR", DefaultValue = "Magenta")]
        public string ADRColor { get; set; }
        [Parameter("ADR Thickess", Group = "ADR", DefaultValue = 1)]
        public int ADRThc { get; set; }
        [Parameter("ADR LineStyle", Group = "ADR", DefaultValue = LineStyle.Solid)]
        public LineStyle ADRLS { get; set; }

        [Parameter("POT", Group = "Power Of Three", DefaultValue = true)]
        public bool POT { get; set; }
        [Parameter("POT Color 50%", Group = "Power Of Three", DefaultValue = "White")]
        public string POTColor50 { get; set; }
        [Parameter("POT Color 200%", Group = "Power Of Three", DefaultValue = "Silver")]
        public string POTColor200 { get; set; }
        [Parameter("POT Thickess", Group = "Power Of Three", DefaultValue = 1)]
        public int POTThc { get; set; }
        [Parameter("POT LineStyle", Group = "Power Of Three", DefaultValue = LineStyle.LinesDots)]
        public LineStyle POTLS { get; set; }

        [Parameter("TimeZone", DefaultValue = 2)]
        public int TZ { get; set; }

        [Parameter("ATR Period", DefaultValue = 14)]
        public int atr_period { get; set; }

        [Parameter("Enable", Group = "Telegram Alerts Settings", DefaultValue = false)]
        public bool SendTelegramAlerts { get; set; }
        [Parameter("Token", Group = "Telegram Alerts Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string TelegramToken { get; set; }
        [Parameter("ChatId", Group = "Telegram Alerts Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string TelegramChatId { get; set; }

        [Output("Signal Ma", LineColor = "RoyalBlue", Thickness = 1)]
        public IndicatorDataSeries SignalMa { get; set; }
        [Output("Baseline Ma", LineColor = "IndianRed", Thickness = 1)]
        public IndicatorDataSeries BaselineMa { get; set; }
        [Output("Short Ma", LineColor = "Yellow", Thickness = 1)]
        public IndicatorDataSeries ShortMa { get; set; }
        [Output("Long Ma", LineColor = "Purple", Thickness = 1)]
        public IndicatorDataSeries LongMa { get; set; }


        private Color AsiaColorWAlpha, AsiaLevelColorWAlpha, BrinksColorWAlpha, Brinks2ColorWAlpha, USColorWAlpha;
        private DateTime AsiaStart, AsiaEnd;

        private Bars DailySeries;
        private Bars WeeklyBars;
        private double Adr_Value;

        private Canvas _panelCanvas = null;
        private TextBlock _header, _values;

        private MovingAverage _iSignal, _iBaseline, _iShort, _iLong;
        private TelegramBot _telegram;

        private void SetDates(int index)
        {
            if (Bars.OpenTimes[index].Hour < 6)
            {

                DateTime PrevDay = Bars.OpenTimes[index].AddDays(-1);
                DateTime CurrentDay = Bars.OpenTimes[index];
                AsiaStart = new DateTime(PrevDay.Year, PrevDay.Month, PrevDay.Day, 22, 0, 0);
                AsiaEnd = new DateTime(CurrentDay.Year, CurrentDay.Month, CurrentDay.Day, 6, 0, 0);
            }
            else if (Bars.OpenTimes[index].Hour >= 22)
            {
                DateTime PrevDay = Bars.OpenTimes[index];
                DateTime CurrentDay = Bars.OpenTimes[index].AddDays(1);
                AsiaStart = new DateTime(PrevDay.Year, PrevDay.Month, PrevDay.Day, 22, 0, 0);
                AsiaEnd = new DateTime(CurrentDay.Year, CurrentDay.Month, CurrentDay.Day, 6, 0, 0);
            }
        }

        private Canvas CreatePanel()
        {
            var canvas = new Canvas();
            canvas.Margin = "0 5";
            canvas.Width = 120;
            canvas.Height = 60;

            _header = new TextBlock();
            _header.Margin = 5;
            _header.FontSize = 12;
            _header.FontWeight = FontWeight.Bold;
            _header.Opacity = 1;
            _header.ForegroundColor = Color.Lime;
            _header.TextAlignment = TextAlignment.Left;
            _header.VerticalAlignment = VerticalAlignment.Top;
            _header.Text = "HOD\nLOD\nTDR\nYDR\nWR\nWH\nWL\nLWH\nLWL\nADR\nTo ADR-H\nTo ADR-L";

            _values = new TextBlock();
            _values.Margin = 5;
            _values.FontSize = 12;
            _values.FontWeight = FontWeight.Normal;
            _values.Opacity = 1;
            _values.ForegroundColor = Color.White;
            _values.TextAlignment = TextAlignment.Left;
            _values.VerticalAlignment = VerticalAlignment.Top;

            var grid = new Grid(1, 1);
            grid.Rows[0].SetHeightToAuto();

            grid.AddChild(canvas, 0, 0, 3, 1);

            grid.AddChild(_header, 0, 0, 3, 1);
            grid.AddChild(_values, 0, 0, 3, 1);

            var border = new Border();
            border.BorderThickness = 1;
            border.BorderColor = Color.Gray;
            border.Margin = 10;
            border.VerticalAlignment = VerticalAlignment.Top;
            border.HorizontalAlignment = HorizontalAlignment.Left;
            border.Child = grid;

            var gridStyle = new Style();
            gridStyle.Set(ControlProperty.BackgroundColor, Color.FromArgb(32, 32, 32));
            gridStyle.Set(ControlProperty.Opacity, 1);
            gridStyle.Set(ControlProperty.Opacity, 0.25, ControlState.Hover);

            grid.Style = gridStyle;

            Chart.AddControl(border);
            return canvas;
        }

        private void updatePanel(int index)
        {
            int DailyIndex = DailySeries.OpenTimes.GetIndexByTime(Bars.OpenTimes[index]);
            int WeeklyIndex = WeeklyBars.OpenTimes.GetIndexByTime(Bars.OpenTimes[index]);
            double range_today = Math.Round((DailySeries.HighPrices[DailyIndex] - DailySeries.LowPrices[DailyIndex]) * Math.Pow(10, Symbol.Digits - 1), 1);
            double range_yesterday = Math.Round((DailySeries.HighPrices[DailyIndex - 1] - DailySeries.LowPrices[DailyIndex - 1]) * Math.Pow(10, Symbol.Digits - 1), 1);
            double range_weekly = Math.Round((WeeklyBars.HighPrices[WeeklyIndex] - WeeklyBars.LowPrices[WeeklyIndex]) * Math.Pow(10, Symbol.Digits - 1), 1);
            double to_adr_high = Math.Round(((DailySeries.OpenPrices.LastValue + Adr_Value * Symbol.PipSize) - DailySeries.ClosePrices.LastValue) / Symbol.PipSize, 0);
            double to_adr_low = Math.Round((DailySeries.ClosePrices.LastValue - (DailySeries.OpenPrices.LastValue - Adr_Value * Symbol.PipSize)) / Symbol.PipSize, 0);

            _values.Text = "\t\t" + DailySeries.HighPrices[DailyIndex] + "\n\t\t" + DailySeries.LowPrices[DailyIndex] + "\n\t\t" + range_today + "\n\t\t" + range_yesterday + "\n\t\t" + range_weekly + "\n\t\t" + WeeklyBars.HighPrices[WeeklyIndex] + "\n\t\t" + WeeklyBars.LowPrices[WeeklyIndex] + "\n\t\t" + WeeklyBars.HighPrices[WeeklyIndex - 1] + "\n\t\t" + WeeklyBars.LowPrices[WeeklyIndex - 1] + "\n\t\t" + Adr_Value + "\n\t\t" + to_adr_high + "\n\t\t" + to_adr_low;
        }

        protected override void Initialize()
        {
            BoxOpt = (int)(255 * BoxOpt * 0.01);
            AsiaLevelsOpt = (int)(255 * AsiaLevelsOpt * 0.01);
            BrinksOpt = (int)(255 * BrinksOpt * 0.01);
            Brinks2Opt = (int)(255 * Brinks2Opt * 0.01);
            USOpt = (int)(255 * USOpt * 0.01);
            AsiaColorWAlpha = Color.FromArgb(BoxOpt, Color.FromName(AsiaColor).R, Color.FromName(AsiaColor).G, Color.FromName(AsiaColor).B);
            AsiaLevelColorWAlpha = Color.FromArgb(AsiaLevelsOpt, Color.FromName(AsiaLevelsColor).R, Color.FromName(AsiaLevelsColor).G, Color.FromName(AsiaLevelsColor).B);
            BrinksColorWAlpha = Color.FromArgb(BrinksOpt, Color.FromName(BrinksColor).R, Color.FromName(BrinksColor).G, Color.FromName(BrinksColor).B);
            Brinks2ColorWAlpha = Color.FromArgb(Brinks2Opt, Color.FromName(Brinks2Color).R, Color.FromName(Brinks2Color).G, Color.FromName(Brinks2Color).B);
            USColorWAlpha = Color.FromArgb(USOpt, Color.FromName(USColor).R, Color.FromName(USColor).G, Color.FromName(USColor).B);

            AsiaZoneDist *= Symbol.PipSize;
            AsiaZoneWidth *= Symbol.PipSize;

            DailySeries = MarketData.GetBars(TimeFrame.Daily);
            WeeklyBars = MarketData.GetBars(TimeFrame.Weekly);


            AverageTrueRange atr = Indicators.AverageTrueRange(DailySeries, atr_period, MovingAverageType.Simple);

            Adr_Value = Math.Round(atr.Result.Last(1) / Symbol.PipSize, 0);

            if (_panelCanvas == null)
            {
                _panelCanvas = CreatePanel();
            }

            _iSignal = Indicators.MovingAverage(Bars.ClosePrices, SignalMaPeriod, SignaltMaType);
            _iBaseline = Indicators.MovingAverage(Bars.ClosePrices, BaselineMaPeriod, BaselineMaType);
            _iShort = Indicators.MovingAverage(Bars.ClosePrices, ShortMaPeriod, ShortMaType);
            _iLong = Indicators.MovingAverage(Bars.ClosePrices, LongMaPeriod, LongMaType);

            _telegram = new TelegramBot(TelegramToken, TelegramChatId, Symbol.Name, TimeFrame.Name);
        }

        public bool DailyRangeDrawn = false;

        public override void Calculate(int index)
        {
            updatePanel(index);

            if (IsLastBar)
            {
                int DailyIndex = DailySeries.OpenTimes.GetIndexByTime(Bars.OpenTimes[index]);
                DrawDaily(index, DailyIndex);
            }

            if (POT && Bars.OpenTimes[index] == AsiaStart.AddHours(1 + TZ))
                DrawPOT(index - 1);

            if (Bars.OpenTimes[index].Hour < 6 || Bars.OpenTimes[index].Hour >= 22)
            {
                SetDates(index);
                DrawAsiaSession(index);
            }
            if (Bars.OpenTimes[index] >= AsiaStart.AddHours(8 + TZ).AddMinutes(15) && Bars.OpenTimes[index] <= AsiaStart.AddHours(9 + TZ).AddMinutes(0))
            {
                DrawBrinksBox(index);
            }
            if (Bars.OpenTimes[index] >= AsiaStart.AddHours(14 + TZ).AddMinutes(15) && Bars.OpenTimes[index] <= AsiaStart.AddHours(14 + TZ).AddMinutes(45))
            {
                DrawBrinksBox2(index);
            }
            if (Bars.OpenTimes[index] >= AsiaStart.AddHours(14 + TZ).AddMinutes(45) && Bars.OpenTimes[index] <= AsiaStart.AddHours(18 + TZ))
            {
                DrawUSSession(index);
            }

            if (Bars.OpenTimes[index - 1].Day != Bars.OpenTimes[index].Day)
                DailyRangeDrawn = false;

            if (!DailyRangeDrawn)
            {
                int DailyIndex = DailySeries.OpenTimes.GetIndexByTime(Bars.OpenTimes[index]);
                DrawADR(index, DailyIndex);
                DrawDaily(index, DailyIndex);

                DailyRangeDrawn = true;
            }

            SignalMa[index] = _iSignal.Result[index];
            BaselineMa[index] = _iBaseline.Result[index];
            ShortMa[index] = _iShort.Result[index];
            LongMa[index] = _iLong.Result[index];

            if (IsLastBar && SendTelegramAlerts && _iSignal.Result.Last(1) > _iBaseline.Result.Last(1) && _iSignal.Result.Last(2) < _iBaseline.Result.Last(2))
                _telegram.SendTextMessage(string.Format("Signal Ma (Period = {0}) Crossed Above Baseline Ma (Period = {1})", SignalMaPeriod, BaselineMaPeriod));
            if (IsLastBar && SendTelegramAlerts && _iSignal.Result.Last(1) < _iBaseline.Result.Last(1) && _iSignal.Result.Last(2) > _iBaseline.Result.Last(2))
                _telegram.SendTextMessage(string.Format("Signal Ma (Period = {0}) Crossed Below Baseline Ma (Period = {1})", SignalMaPeriod, BaselineMaPeriod));
        }

        private void DrawADR(int index, int DailyIndex)
        {
            Chart.DrawTrendLine("ADR High " + DailyIndex, DailySeries.OpenTimes[DailyIndex], DailySeries.OpenPrices[DailyIndex] + Adr_Value * Symbol.PipSize, DailySeries.OpenTimes[DailyIndex].AddDays(1), DailySeries.OpenPrices[DailyIndex] + Adr_Value * Symbol.PipSize, Color.FromName(ADRColor), ADRThc, ADRLS);
            Chart.DrawTrendLine("ADR Low " + DailyIndex, DailySeries.OpenTimes[DailyIndex], DailySeries.OpenPrices[DailyIndex] - Adr_Value * Symbol.PipSize, DailySeries.OpenTimes[DailyIndex].AddDays(1), DailySeries.OpenPrices[DailyIndex] - Adr_Value * Symbol.PipSize, Color.FromName(ADRColor), ADRThc, ADRLS);
            Chart.DrawText("ADR High Label", "ADR H " + (DailySeries.OpenPrices[DailyIndex] + Adr_Value * Symbol.PipSize), DailySeries.OpenTimes[DailyIndex].AddHours(3), DailySeries.OpenPrices[DailyIndex] + Adr_Value * Symbol.PipSize, Color.FromName(ADRColor));
            Chart.DrawText("ADR Low Label", "ADR L " + (DailySeries.OpenPrices[DailyIndex] - Adr_Value * Symbol.PipSize), DailySeries.OpenTimes[DailyIndex].AddHours(3), DailySeries.OpenPrices[DailyIndex] - Adr_Value * Symbol.PipSize, Color.FromName(ADRColor));

        }

        private void DrawDaily(int index, int DailyIndex)
        {
            Chart.DrawTrendLine("Daily High " + DailyIndex, DailySeries.OpenTimes[DailyIndex], DailySeries.HighPrices[DailyIndex - 1], DailySeries.OpenTimes[DailyIndex].AddDays(1), DailySeries.HighPrices[DailyIndex - 1], Color.FromName(DailyColor), DailyThc, DailyLS);
            Chart.DrawTrendLine("Daily Low " + DailyIndex, DailySeries.OpenTimes[DailyIndex], DailySeries.LowPrices[DailyIndex - 1], DailySeries.OpenTimes[DailyIndex].AddDays(1), DailySeries.LowPrices[DailyIndex - 1], Color.FromName(DailyColor), DailyThc, DailyLS);
            Chart.DrawText("Daily High Label", "YH " + DailySeries.HighPrices[DailyIndex - 1], DailySeries.OpenTimes[DailyIndex], DailySeries.HighPrices[DailyIndex - 1], Color.FromName(DailyColor));
            Chart.DrawText("Daily Low Label", "YL " + DailySeries.LowPrices[DailyIndex - 1], DailySeries.OpenTimes[DailyIndex], DailySeries.LowPrices[DailyIndex - 1], Color.FromName(DailyColor));
        }
//
//              Drawing Asia Session
//
        private void DrawAsiaSession(int index)
        {
            double AsiaMax = FindAsiaMax(index);
            double AsiaMin = FindAsiaMin(index);

            string RectangleLabel = "AsiaSession" + AsiaStart.Day + " " + AsiaStart.Month + " " + AsiaStart.Year;
            Chart.DrawRectangle(RectangleLabel, AsiaStart, AsiaMax, AsiaEnd, AsiaMin, AsiaColorWAlpha).IsFilled = true;
            Chart.DrawText(RectangleLabel + " Pips", "R = " + Math.Round((AsiaMax - AsiaMin) / Symbol.PipSize, 2), AsiaStart, AsiaMin, AsiaColor);

            DateTime AsiaLastQuarterStart = DrawAsiaBoxDivision(AsiaMax, AsiaMin);
            if (AsiaMax - AsiaMin < StopHuntPips * Symbol.PipSize || StopHuntPips == -1)
                DrawAsiaRangeZones(AsiaMax, AsiaMin);
            else
                DrawAsiaRangeZoneStopHunt(AsiaLastQuarterStart);
            DrawAsiaLevels(AsiaMax, AsiaMin);
        }

        private double FindAsiaMax(int index)
        {
            int AsiaStartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart);
            double AsiaMax = 0;
            while (index >= AsiaStartIndex)
            {
                AsiaMax = Math.Max(AsiaMax, Bars.HighPrices[index]);
                index--;
            }
            return AsiaMax;
        }

        private double FindAsiaMin(int index)
        {
            int AsiaStartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart);
            double AsiaMin = double.PositiveInfinity;
            while (index >= AsiaStartIndex)
            {
                AsiaMin = Math.Min(AsiaMin, Bars.LowPrices[index]);
                index--;
            }
            return AsiaMin;
        }

        private void DrawAsiaRangeZones(double AsiaMax, double AsiaMin)
        {
            Chart.DrawRectangle("AsiaUpperZone " + AsiaEnd, AsiaEnd, AsiaMax + AsiaZoneDist, AsiaEnd.AddHours(6 + TZ).AddMinutes(30), AsiaMax + AsiaZoneDist + AsiaZoneWidth, AsiaColorWAlpha).IsFilled = true;
            Chart.DrawRectangle("AsiaLowerZone " + AsiaEnd, AsiaEnd, AsiaMin - AsiaZoneDist, AsiaEnd.AddHours(6 + TZ).AddMinutes(30), AsiaMin - AsiaZoneDist - AsiaZoneWidth, AsiaColorWAlpha).IsFilled = true;
        }

        private void DrawAsiaRangeZoneStopHunt(DateTime AsiaLastQuarterStart)
        {
            int AsiaLastQuarterStartIndex = Bars.OpenTimes.GetIndexByTime(AsiaLastQuarterStart);
            int index = Bars.OpenTimes.GetIndexByTime(AsiaEnd);
            double LastQuarterMax = 0;
            double LastQuarterMin = double.PositiveInfinity;
            while (index >= AsiaLastQuarterStartIndex)
            {
                LastQuarterMax = Math.Max(LastQuarterMax, Bars.HighPrices[index]);
                LastQuarterMin = Math.Min(LastQuarterMin, Bars.LowPrices[index]);
                index--;
            }
            Chart.DrawRectangle("AsiaUpperZone " + AsiaEnd, AsiaEnd, LastQuarterMax + AsiaZoneDist, AsiaEnd.AddHours(6 + TZ).AddMinutes(30), LastQuarterMax + AsiaZoneDist + AsiaZoneWidth, Color.FromArgb(BoxOpt, 255, 0, 0), 2, LineStyle.Lines).IsFilled = true;
            Chart.DrawRectangle("AsiaLowerZone " + AsiaEnd, AsiaEnd, LastQuarterMin - AsiaZoneDist, AsiaEnd.AddHours(6 + TZ).AddMinutes(30), LastQuarterMin - AsiaZoneDist - AsiaZoneWidth, Color.FromArgb(BoxOpt, 255, 0, 0), 2, LineStyle.Lines).IsFilled = true;
            Chart.DrawRectangle("AsiaLastQuarter " + AsiaEnd, AsiaLastQuarterStart, LastQuarterMax, AsiaEnd, LastQuarterMin, Color.Red);
        }

        private void DrawAsiaLevels(double AsiaMax, double AsiaMin)
        {
            Chart.DrawTrendLine("Asia Top Level" + AsiaEnd, AsiaEnd, AsiaMax, AsiaEnd.AddHours(8), AsiaMax, AsiaLevelColorWAlpha, AsiaLevelsThc, AsiaLevelsLS);
            Chart.DrawTrendLine("Asia Mid Level" + AsiaEnd, AsiaEnd, (AsiaMax + AsiaMin) / 2, AsiaEnd.AddHours(8), (AsiaMax + AsiaMin) / 2, AsiaLevelColorWAlpha, AsiaLevelsThc, AsiaLevelsLS);
            Chart.DrawTrendLine("Asia Bottom Level" + AsiaEnd, AsiaEnd, AsiaMin, AsiaEnd.AddHours(8), AsiaMin, AsiaLevelColorWAlpha, AsiaLevelsThc, AsiaLevelsLS);
        }

        private DateTime DrawAsiaBoxDivision(double AsiaMax, double AsiaMin)
        {
            int MinutesInAsiaSession = 0;
            while (AsiaStart.AddMinutes(MinutesInAsiaSession) < AsiaEnd)
                MinutesInAsiaSession++;
            MinutesInAsiaSession = (int)(MinutesInAsiaSession / 4);
            for (int i = 1; i < 4; ++i)
            {
                Chart.DrawTrendLine("Asia Divisor " + i + " " + AsiaEnd, AsiaStart.AddMinutes(MinutesInAsiaSession * i), AsiaMax, AsiaStart.AddMinutes(MinutesInAsiaSession * i), AsiaMin, AsiaLevelColorWAlpha, 1, AsiaLevelsLS);
            }
            return AsiaStart.AddMinutes(MinutesInAsiaSession * 3);
        }

        private Tuple<double, double> GetPOTRange(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(-5 + TZ));

            double Max = 0;
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, Bars.HighPrices[index]);
                Min = Math.Min(Min, Bars.LowPrices[index]);
                index--;
            }
            return Tuple.Create(Max, Min);
        }

        private Tuple<double, double> CalculatePOT(Tuple<double, double> range, double percentage)
        {
            double deviation = (range.Item1 - range.Item2) * (percentage / 100.0);

            double h1 = range.Item1 + deviation / 2;
            double h2 = range.Item1 + deviation;
            double h3 = (h1 + h2) / 2;

            double l1 = range.Item2 - deviation / 2;
            double l2 = range.Item2 - deviation;
            double l3 = (l1 + l2) / 2;

            return Tuple.Create(h3, l3);
        }

        private void DrawPOT(int index)
        {
            Tuple<double, double> _range = GetPOTRange(index);

            Tuple<double, double> _values50 = CalculatePOT(_range, 50.0);
            Tuple<double, double> _values200 = CalculatePOT(_range, 200.0);

            Chart.DrawTrendLine("POT UP 50" + index, AsiaStart.AddHours(1 + TZ), _values50.Item1, AsiaStart.AddHours(19 + TZ), _values50.Item1, Color.FromName(POTColor50), POTThc, POTLS);
            Chart.DrawTrendLine("POT DOWN 50" + index, AsiaStart.AddHours(1 + TZ), _values50.Item2, AsiaStart.AddHours(19 + TZ), _values50.Item2, Color.FromName(POTColor50), POTThc, POTLS);

            Chart.DrawTrendLine("POT UP 200" + index, AsiaStart.AddHours(1 + TZ), _values200.Item1, AsiaStart.AddHours(19 + TZ), _values200.Item1, Color.FromName(POTColor200), POTThc, POTLS);
            Chart.DrawTrendLine("POT DOWN 200" + index, AsiaStart.AddHours(1 + TZ), _values200.Item2, AsiaStart.AddHours(19 + TZ), _values200.Item2, Color.FromName(POTColor200), POTThc, POTLS);
        }

//
//              End Asia Session
//

//
//              Brinks Box 1
//
        private void DrawBrinksBox(int index)
        {
            double Max = FindBrinksMax(index);
            double Min = FindBrinksMin(index);

            Chart.DrawRectangle("Brinks Area " + AsiaStart, AsiaStart.AddHours(8 + TZ), Max, AsiaStart.AddHours(9 + TZ), Min, BrinksColorWAlpha).IsFilled = true;
            Chart.DrawText("Brinks Area Pips " + AsiaStart, "" + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(10), Min, Color.FromName(BrinksColor));
        }

        private double FindBrinksMax(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(8 + TZ).AddMinutes(15));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, Bars.HighPrices[index]);
                index--;
            }
            return Max;
        }

        private double FindBrinksMin(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(8 + TZ).AddMinutes(15));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, Bars.LowPrices[index]);
                index--;
            }
            return Min;
        }
//
//              End Brinks Box 1
//

//
//              Brinks Box 2
//
        private void DrawBrinksBox2(int index)
        {
            double Max = FindBrinks2Max(index);
            double Min = FindBrinks2Min(index);

            Chart.DrawRectangle("Brinks Area 2 " + AsiaStart, AsiaStart.AddHours(14 + TZ), Max, AsiaStart.AddHours(15 + TZ), Min, Brinks2ColorWAlpha).IsFilled = true;
            Chart.DrawText("Brinks Area Pips 2 " + AsiaStart, "" + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(14 + TZ), Min, Color.FromName(Brinks2Color));
        }

        private double FindBrinks2Max(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(14 + TZ).AddMinutes(15));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, Bars.HighPrices[index]);
                index--;
            }
            return Max;
        }

        private double FindBrinks2Min(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(14 + TZ).AddMinutes(15));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, Bars.LowPrices[index]);
                index--;
            }
            return Min;
        }
//
//              End Brinks Box 2
//

//
//              US Session
//
        private void DrawUSSession(int index)
        {
            double Max = FindUSMax(index);
            double Min = FindUSMin(index);

            Chart.DrawRectangle("US Area " + AsiaStart, AsiaStart.AddHours(14 + TZ).AddMinutes(30), Max, AsiaStart.AddHours(18 + TZ), Min, USColorWAlpha).IsFilled = true;
            Chart.DrawText("US Area Pips " + AsiaStart, "R = " + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(15 + TZ), Min, Color.FromName(USColor));
        }

        private double FindUSMax(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(14 + TZ).AddMinutes(45));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, Bars.HighPrices[index]);
                index--;
            }
            return Max;
        }

        private double FindUSMin(int index)
        {
            int StartIndex = Bars.OpenTimes.GetIndexByTime(AsiaStart.AddHours(14 + TZ).AddMinutes(45));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, Bars.LowPrices[index]);
                index--;
            }
            return Min;
        }
//
//              End US Session
//
    }

    public class TelegramBot
    {
        // Chat bots attribute
        private readonly string _defaultUrl;

        // Constructor
        public TelegramBot(string token, string defaultChatId, string symbol, string timeframe)
        {
            _defaultUrl = string.Format("https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text=[{2}-{3}] ", token, defaultChatId, symbol, timeframe);
            ServicePointManager.Expect100Continue = true;
            ServicePointManager.DefaultConnectionLimit = 1000000;
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        }

        // Send a telegram message to the default chat id
        public void SendTextMessage(string message)
        {
            WebRequest.Create(_defaultUrl + message).GetResponse();
        }
    }
}
