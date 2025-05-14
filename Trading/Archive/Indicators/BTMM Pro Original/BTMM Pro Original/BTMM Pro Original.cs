using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class BTMMProOriginal : Indicator
    {
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
        [Parameter("Asia Levels Opacity", Group = "Asia Levels", DefaultValue = 20)]
        public int AsiaLevelsOpt { get; set; }
        [Parameter("Asia Levels Color", Group = "Asia Levels", DefaultValue = "Yellow")]
        public string AsiaLevelsColor { get; set; }

        [Parameter("Brinks Color", Group = "Brinks Box", DefaultValue = "Green")]
        public string BrinksColor { get; set; }
        [Parameter("Brinks Opacity", Group = "Brinks Box", DefaultValue = 20)]
        public int BrinksOpt { get; set; }

        [Parameter("Brinks 2 Color", Group = "Brinks Box 2", DefaultValue = "Yellow")]
        public string Brinks2Color { get; set; }
        [Parameter("Brinks 2 Opacity", Group = "Brinks Box 2", DefaultValue = 20)]
        public int Brinks2Opt { get; set; }

        [Parameter("US Color", Group = "US Box", DefaultValue = "Red")]
        public string USColor { get; set; }
        [Parameter("US Opacity", Group = "US Box ", DefaultValue = 20)]
        public int USOpt { get; set; }

        [Parameter("Daily Range Color", Group = "Daily Range", DefaultValue = "RoyalBlue")]
        public string DailyColor { get; set; }
        [Parameter("Daily Range Thickess", Group = "Daily Range", DefaultValue = 1)]
        public int DailyThc { get; set; }
        [Parameter("Daily Range LineStyle", Group = "Daily Range", DefaultValue = LineStyle.Solid)]
        public LineStyle DailyLS { get; set; }
        [Parameter("ADR Color", Group = "ADR", DefaultValue = "Red")]
        public string ADRColor { get; set; }
        [Parameter("ADR Thickess", Group = "ADR", DefaultValue = 1)]
        public int ADRThc { get; set; }
        [Parameter("ADR LineStyle", Group = "ADR", DefaultValue = LineStyle.Solid)]
        public LineStyle ADRLS { get; set; }

        [Parameter("POT", Group = "Power Of Three", DefaultValue = true)]
        public bool POT { get; set; }
        [Parameter("POT Color", Group = "Power Of Three", DefaultValue = "White")]
        public string POTColor { get; set; }
        [Parameter("POT Thickess", Group = "Power Of Three", DefaultValue = 1)]
        public int POTThc { get; set; }
        [Parameter("POT LineStyle", Group = "Power Of Three", DefaultValue = LineStyle.LinesDots)]
        public LineStyle POTLS { get; set; }

        [Parameter("TimeZone", DefaultValue = 2)]
        public int TZ { get; set; }

        private Color AsiaColorWAlpha, AsiaLevelColorWAlpha, BrinksColorWAlpha, Brinks2ColorWAlpha, USColorWAlpha;
        private DateTime AsiaStart, AsiaEnd;

        private MarketSeries DailySeries;

        private ADR ADR;

        private void SetDates(int index)
        {
            if (MarketSeries.OpenTime[index].Hour < 6)
            {
                DateTime PrevDay = MarketSeries.OpenTime[index].AddDays(-1);
                DateTime CurrentDay = MarketSeries.OpenTime[index];
                AsiaStart = new DateTime(PrevDay.Year, PrevDay.Month, PrevDay.Day, 22, 0, 0);
                AsiaEnd = new DateTime(CurrentDay.Year, CurrentDay.Month, CurrentDay.Day, 6, 0, 0);
            }
            else if (MarketSeries.OpenTime[index].Hour >= 22)
            {
                DateTime PrevDay = MarketSeries.OpenTime[index];
                DateTime CurrentDay = MarketSeries.OpenTime[index].AddDays(1);
                AsiaStart = new DateTime(PrevDay.Year, PrevDay.Month, PrevDay.Day, 22, 0, 0);
                AsiaEnd = new DateTime(CurrentDay.Year, CurrentDay.Month, CurrentDay.Day, 6, 0, 0);
            }
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

            DailySeries = MarketData.GetSeries(TimeFrame.Daily);

            TZ = -TZ;
            TZ += 3;

            ADR = Indicators.GetIndicator<ADR>(5);
        }

        public bool DailyRangeDrawn = false;

        public override void Calculate(int index)
        {
            if (TimeFrame > TimeFrame.Minute30)
                return;
            if (MarketSeries.OpenTime[index].Hour < 6 || MarketSeries.OpenTime[index].Hour >= 22)
            {
                SetDates(index);
                DrawAsiaSession(index);
            }
            if (MarketSeries.OpenTime[index].Hour >= 7 && MarketSeries.OpenTime[index].Hour < 8)
            {
                DrawBrinksBox(index);
            }
            if (MarketSeries.OpenTime[index].Hour >= 13 && MarketSeries.OpenTime[index].Hour < 14)
            {
                DrawBrinksBox2(index);
            }
            if (((MarketSeries.OpenTime[index].Hour >= 13 && MarketSeries.OpenTime[index].Minute >= 30) || MarketSeries.OpenTime[index].Hour >= 14) && MarketSeries.OpenTime[index].Hour < 17)
            {
                DrawUSSession(index);
            }

            if (MarketSeries.OpenTime[index - 1].Day != MarketSeries.OpenTime[index].Day)
                DailyRangeDrawn = false;

            if (!DailyRangeDrawn)
            {
                int DailyIndex = DailySeries.OpenTime.GetIndexByTime(MarketSeries.OpenTime[index]);
                DrawADR(index, DailyIndex);
                DrawDaily(index, DailyIndex);

                DailyRangeDrawn = true;
            }
        }

        private void DrawADR(int index, int DailyIndex)
        {
            Chart.DrawTrendLine("ADR High " + DailyIndex, DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Open[DailyIndex] + ADR.ADR5[index] * Symbol.PipSize, DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), DailySeries.Open[DailyIndex] + ADR.ADR5[index] * Symbol.PipSize, Color.FromName(ADRColor), ADRThc, ADRLS);
            Chart.DrawTrendLine("ADR Low " + DailyIndex, DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Open[DailyIndex] - ADR.ADR5[index] * Symbol.PipSize, DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), DailySeries.Open[DailyIndex] - ADR.ADR5[index] * Symbol.PipSize, Color.FromName(ADRColor), ADRThc, ADRLS);
            Chart.DrawText("ADR High Label", "ADR H " + (DailySeries.Open[DailyIndex] + ADR.ADR5[index] * Symbol.PipSize), DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Open[DailyIndex] + ADR.ADR5[index] * Symbol.PipSize, Color.FromName(ADRColor));
            Chart.DrawText("ADR Low Label", "ADR L " + (DailySeries.Open[DailyIndex] - ADR.ADR5[index] * Symbol.PipSize), DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Open[DailyIndex] - ADR.ADR5[index] * Symbol.PipSize, Color.FromName(ADRColor));

        }

        private void DrawDaily(int index, int DailyIndex)
        {
            Chart.DrawTrendLine("Daily High " + DailyIndex, DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.High[DailyIndex - 1], DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), DailySeries.High[DailyIndex - 1], Color.FromName(DailyColor), DailyThc, DailyLS);
            Chart.DrawTrendLine("Daily Low " + DailyIndex, DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Low[DailyIndex - 1], DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), DailySeries.Low[DailyIndex - 1], Color.FromName(DailyColor), DailyThc, DailyLS);
            Chart.DrawText("Daily High Label", "YH " + DailySeries.High[DailyIndex - 1], DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.High[DailyIndex - 1], Color.FromName(DailyColor));
            Chart.DrawText("Daily Low Label", "YL " + DailySeries.Low[DailyIndex - 1], DailySeries.OpenTime[DailyIndex].AddHours(TZ), DailySeries.Low[DailyIndex - 1], Color.FromName(DailyColor));
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
            Chart.DrawText(RectangleLabel + " Pips", "PIPS: " + Math.Round((AsiaMax - AsiaMin) / Symbol.PipSize, 2), AsiaStart, AsiaMin, AsiaColor);

            DateTime AsiaLastQuarterStart = DrawAsiaBoxDivision(AsiaMax, AsiaMin);
            if (AsiaMax - AsiaMin < StopHuntPips * Symbol.PipSize || StopHuntPips == -1)
                DrawAsiaRangeZones(AsiaMax, AsiaMin);
            else
                DrawAsiaRangeZoneStopHunt(AsiaLastQuarterStart);
            DrawAsiaLevels(AsiaMax, AsiaMin);
            if (POT)
                DrawPOT(AsiaLastQuarterStart, index);
        }

        private double FindAsiaMax(int index)
        {
            int AsiaStartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart);
            double AsiaMax = 0;
            while (index >= AsiaStartIndex)
            {
                AsiaMax = Math.Max(AsiaMax, MarketSeries.High[index]);
                index--;
            }
            return AsiaMax;
        }

        private double FindAsiaMin(int index)
        {
            int AsiaStartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart);
            double AsiaMin = double.PositiveInfinity;
            while (index >= AsiaStartIndex)
            {
                AsiaMin = Math.Min(AsiaMin, MarketSeries.Low[index]);
                index--;
            }
            return AsiaMin;
        }

        private void DrawAsiaRangeZones(double AsiaMax, double AsiaMin)
        {
            Chart.DrawRectangle("AsiaUpperZone " + AsiaEnd, AsiaEnd, AsiaMax + AsiaZoneDist, AsiaEnd.AddHours(7), AsiaMax + AsiaZoneDist + AsiaZoneWidth, AsiaColorWAlpha).IsFilled = true;
            Chart.DrawRectangle("AsiaLowerZone " + AsiaEnd, AsiaEnd, AsiaMin - AsiaZoneDist, AsiaEnd.AddHours(7), AsiaMin - AsiaZoneDist - AsiaZoneWidth, AsiaColorWAlpha).IsFilled = true;
        }

        private void DrawAsiaRangeZoneStopHunt(DateTime AsiaLastQuarterStart)
        {
            int AsiaLastQuarterStartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaLastQuarterStart);
            int index = MarketSeries.OpenTime.GetIndexByTime(AsiaEnd);
            double LastQuarterMax = 0;
            double LastQuarterMin = double.PositiveInfinity;
            while (index >= AsiaLastQuarterStartIndex)
            {
                LastQuarterMax = Math.Max(LastQuarterMax, MarketSeries.High[index]);
                LastQuarterMin = Math.Min(LastQuarterMin, MarketSeries.Low[index]);
                index--;
            }
            Chart.DrawRectangle("AsiaUpperZone " + AsiaEnd, AsiaEnd, LastQuarterMax + AsiaZoneDist, AsiaEnd.AddHours(7), LastQuarterMax + AsiaZoneDist + AsiaZoneWidth, Color.FromArgb(BoxOpt, 255, 0, 0), 2, LineStyle.Lines).IsFilled = true;
            Chart.DrawRectangle("AsiaLowerZone " + AsiaEnd, AsiaEnd, LastQuarterMin - AsiaZoneDist, AsiaEnd.AddHours(7), LastQuarterMin - AsiaZoneDist - AsiaZoneWidth, Color.FromArgb(BoxOpt, 255, 0, 0), 2, LineStyle.Lines).IsFilled = true;
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

        private void DrawPOT(DateTime AsiaLastQuarterStart, int ChartIndex)
        {
            int AsiaStartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart);
            int index = MarketSeries.OpenTime.GetIndexByTime(AsiaLastQuarterStart);
            int DailyIndex = DailySeries.OpenTime.GetIndexByTime(MarketSeries.OpenTime[ChartIndex]);
            double ThreeQuarterMax = 0;
            double ThreeQuarterMin = double.PositiveInfinity;
            while (index >= AsiaStartIndex)
            {
                ThreeQuarterMax = Math.Max(ThreeQuarterMax, MarketSeries.High[index]);
                ThreeQuarterMin = Math.Min(ThreeQuarterMin, MarketSeries.Low[index]);
                index--;
            }
            for (int i = 1; i <= 3; ++i)
            {
                Chart.DrawTrendLine("POT UP" + i + " " + AsiaEnd, DailySeries.OpenTime[DailyIndex].AddHours(TZ), ThreeQuarterMax + (ThreeQuarterMax - ThreeQuarterMin) * i, DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), ThreeQuarterMax + (ThreeQuarterMax - ThreeQuarterMin) * i, Color.FromName(POTColor), POTThc, POTLS);
                Chart.DrawTrendLine("POT DOWN" + i + " " + AsiaEnd, DailySeries.OpenTime[DailyIndex].AddHours(TZ), ThreeQuarterMin - (ThreeQuarterMax - ThreeQuarterMin) * i, DailySeries.OpenTime[DailyIndex].AddDays(1).AddHours(TZ), ThreeQuarterMin - (ThreeQuarterMax - ThreeQuarterMin) * i, Color.FromName(POTColor), POTThc, POTLS);
            }
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

            Chart.DrawRectangle("Brinks Area " + AsiaStart, AsiaStart.AddHours(9), Max, AsiaStart.AddHours(10), Min, BrinksColorWAlpha).IsFilled = true;
            Chart.DrawText("Brinks Area Pips " + AsiaStart, "PIPS: " + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(9), Min, Color.FromName(BrinksColor));
        }

        private double FindBrinksMax(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(9));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, MarketSeries.High[index]);
                index--;
            }
            return Max;
        }

        private double FindBrinksMin(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(9));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, MarketSeries.Low[index]);
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

            Chart.DrawRectangle("Brinks Area 2 " + AsiaStart, AsiaStart.AddHours(15), Max, AsiaStart.AddHours(16), Min, Brinks2ColorWAlpha).IsFilled = true;
            Chart.DrawText("Brinks Area Pips 2 " + AsiaStart, "PIPS: " + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(15), Min, Color.FromName(Brinks2Color));
        }

        private double FindBrinks2Max(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(15));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, MarketSeries.High[index]);
                index--;
            }
            return Max;
        }

        private double FindBrinks2Min(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(15));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, MarketSeries.Low[index]);
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

            Chart.DrawRectangle("US Area " + AsiaStart, AsiaStart.AddHours(15).AddMinutes(30), Max, AsiaStart.AddHours(19), Min, USColorWAlpha).IsFilled = true;
            Chart.DrawText("US Area Pips " + AsiaStart, "PIPS: " + Math.Round((Max - Min) / Symbol.PipSize, 2), AsiaStart.AddHours(15).AddMinutes(30), Min, Color.FromName(USColor));
        }

        private double FindUSMax(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(15).AddMinutes(30));
            double Max = 0;
            while (index >= StartIndex)
            {
                Max = Math.Max(Max, MarketSeries.High[index]);
                index--;
            }
            return Max;
        }

        private double FindUSMin(int index)
        {
            int StartIndex = MarketSeries.OpenTime.GetIndexByTime(AsiaStart.AddHours(15).AddMinutes(30));
            double Min = double.PositiveInfinity;
            while (index >= StartIndex)
            {
                Min = Math.Min(Min, MarketSeries.Low[index]);
                index--;
            }
            return Min;
        }
//
//              End US Session
//
    }
}
