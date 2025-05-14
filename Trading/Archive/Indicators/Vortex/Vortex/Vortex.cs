using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class Vortex : Indicator
    {
        [Parameter("Periods", DefaultValue = 21)]
        public int per { get; set; }
        [Parameter("HighLight Bubbles", DefaultValue = false)]
        public bool bubble { get; set; }

        [Output("VM+", LineColor = "Cyan")]
        public IndicatorDataSeries vmp { get; set; }
        [Output("VM-", LineColor = "Red")]
        public IndicatorDataSeries vmm { get; set; }

        private IndicatorDataSeries tr, vmPlus, vmMinus;

        protected override void Initialize()
        {
            tr = CreateDataSeries();
            vmPlus = CreateDataSeries();
            vmMinus = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            tr[index] = Math.Max(Math.Max(MarketSeries.High[index] - MarketSeries.Low[index], Math.Abs(MarketSeries.High[index] - MarketSeries.Close[index - 1])), Math.Abs(MarketSeries.Low[index] - MarketSeries.Close[index - 1]));

            vmPlus[index] = Math.Abs(MarketSeries.High[index] - MarketSeries.Low[index - 1]);
            vmMinus[index] = Math.Abs(MarketSeries.Low[index] - MarketSeries.High[index - 1]);

            double sumTR = 0, sumVMP = 0, sumVMM = 0;

            for (int i = 0; i < per; i++)
            {
                sumTR += tr[index - i];
                sumVMP += vmPlus[index - i];
                sumVMM += vmMinus[index - i];
            }

            vmp[index] = sumVMP / sumTR;
            vmm[index] = sumVMM / sumTR;

            if (bubble)
                IndicatorArea.DrawTrendLine("bubble" + index, index, vmp[index], index, vmm[index], vmp[index] > vmm[index] ? Color.Cyan : Color.Red, 3);
        }
    }
}
