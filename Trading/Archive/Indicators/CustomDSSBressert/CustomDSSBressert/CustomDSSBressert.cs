using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;

namespace cAlgo
{
    [Levels(0, 20, 40, 60, 80, 100)]
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None, ScalePrecision = 2)]
    public class CustomDSSBressert : Indicator
    {
        [Parameter("Stochastic period", DefaultValue = 13)]
        public int Stochastic_Period { get; set; }

        [Parameter("EMA period", DefaultValue = 8)]
        public int EMA_Period { get; set; }

        [Parameter("WMA period", DefaultValue = 8)]
        public int WMA_Period { get; set; }

        [Output("DSS", Color = Colors.White, Thickness = 1)]
        public IndicatorDataSeries DSS { get; set; }

        [Output("DSS Up", Color = Colors.DodgerBlue, PlotType = PlotType.Points, Thickness = 5)]
        public IndicatorDataSeries DSS_Up { get; set; }

        [Output("DSS Down", Color = Colors.Red, PlotType = PlotType.Points, Thickness = 5)]
        public IndicatorDataSeries DSS_Down { get; set; }

        [Output("WMA", Color = Colors.Gold, Thickness = 1)]
        public IndicatorDataSeries WmaResult { get; set; }

        [Output("L1", LineStyle = LineStyle.Solid, Color = Colors.LightGray)]
        public IndicatorDataSeries L1 { get; set; }

        [Output("L2", LineStyle = LineStyle.DotsRare, Color = Colors.LightGray)]
        public IndicatorDataSeries L2 { get; set; }

        [Output("L3", LineStyle = LineStyle.DotsRare, Color = Colors.LightGray)]
        public IndicatorDataSeries L3 { get; set; }

        [Output("L4", LineStyle = LineStyle.Solid, Color = Colors.LightGray)]
        public IndicatorDataSeries L4 { get; set; }

        private double Ln = 0;
        private double Hn = 0;
        private double LXn = 0;
        private double HXn = 0;
        private double alpha = 0;
        private IndicatorDataSeries mit;
        private WeightedMovingAverage WMA;

        protected override void Initialize()
        {
            mit = CreateDataSeries();
            alpha = 2.0 / (1.0 + EMA_Period);
            WMA = Indicators.WeightedMovingAverage(DSS, WMA_Period);
        }

        public override void Calculate(int index)
        {
            L1[index] = 20;
            L2[index] = 40;
            L3[index] = 60;
            L4[index] = 80;

            if (double.IsNaN(mit[index - 1]))
            {
                mit[index - 1] = 0;
            }

            if (double.IsNaN(DSS[index - 1]))
            {
                DSS[index - 1] = 0;
            }

            Ln = MarketSeries.Low.Minimum(Stochastic_Period);
            Hn = MarketSeries.High.Maximum(Stochastic_Period);

            mit[index] = mit[index - 1] + alpha * ((((MarketSeries.Close[index] - Ln) / (Hn - Ln)) * 100) - mit[index - 1]);

            LXn = mit.Minimum(Stochastic_Period);
            HXn = mit.Maximum(Stochastic_Period);
            DSS[index] = DSS[index - 1] + alpha * ((((mit[index] - LXn) / (HXn - LXn)) * 100) - DSS[index - 1]);

            if (DSS[index] > DSS[index - 1])
            {
                DSS_Up[index] = DSS[index];
                DSS_Down[index] = double.NaN;
            }

            if (DSS[index] < DSS[index - 1])
            {
                DSS_Down[index] = DSS[index];
                DSS_Up[index] = double.NaN;
            }

            WmaResult[index] = WMA.Result[index];
        }

    }
}
