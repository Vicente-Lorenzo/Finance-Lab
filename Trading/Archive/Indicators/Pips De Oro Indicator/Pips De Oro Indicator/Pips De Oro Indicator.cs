using System;
using cAlgo.API;
using cAlgo.API.Internals;
using cAlgo.API.Indicators;
using cAlgo.Indicators;

namespace cAlgo
{
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class PipsDeOroIndicator : Indicator
    {
        [Parameter("Source", Group = "Signal Moving Average Settings")]
        public DataSeries SignalMaSource { get; set; }
        [Parameter("Period", Group = "Signal Moving Average Settings", DefaultValue = 6)]
        public int SignalMaPeriod { get; set; }
        [Parameter("Type", Group = "Signal Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType SignalMaType { get; set; }

        [Parameter("Source", Group = "Baseline Moving Average Settings")]
        public DataSeries BaselineMaSource { get; set; }
        [Parameter("Period", Group = "Baseline Moving Average Settings", DefaultValue = 30)]
        public int BaselineMaPeriod { get; set; }
        [Parameter("Type", Group = "Baseline Moving Average Settings", DefaultValue = MovingAverageType.Exponential)]
        public MovingAverageType BaselineMaType { get; set; }

        [Parameter("Draw Entry Symbol", Group = "Entry Symbol Settings", DefaultValue = true)]
        public bool UseSymbols { get; set; }
        [Parameter("Buy Symbol Type", Group = "Entry Symbol Settings", DefaultValue = ChartIconType.UpArrow)]
        public ChartIconType BuySymbolType { get; set; }
        [Parameter("Sell Symbol Type", Group = "Entry Symbol Settings", DefaultValue = ChartIconType.DownArrow)]
        public ChartIconType SellSymbolType { get; set; }
        [Parameter("Buy Symbol Color", Group = "Entry Symbol Settings", DefaultValue = "RoyalBlue")]
        public string BuySymbolColorName { get; set; }
        [Parameter("Sell Symbol Color", Group = "Entry Symbol Settings", DefaultValue = "IndianRed")]
        public string SellSymbolColorName { get; set; }
        [Parameter("Symbol Distance (Pips)", Group = "Entry Symbol Settings", DefaultValue = 2)]
        public double SymbolDistancePips { get; set; }

        [Parameter("Draw Level", Group = "Entry Level Settings", DefaultValue = true)]
        public bool DrawEntryLevel { get; set; }
        [Parameter("Level Color", Group = "Entry Level Settings", DefaultValue = "Yellow")]
        public string EntryLevelColor { get; set; }

        [Parameter("Draw Level", Group = "SL Level Settings", DefaultValue = true)]
        public bool DrawStopLossLevel { get; set; }
        [Parameter("Level Multiplier", Group = "SL Level Settings", DefaultValue = 1.0)]
        public double StopLossLevelMultiplier { get; set; }
        [Parameter("Level Color", Group = "SL Level Settings", DefaultValue = "DarkRed")]
        public string StopLossLevelColor { get; set; }

        [Parameter("Draw Level", Group = "TP1 Level Settings", DefaultValue = true)]
        public bool DrawFirstTakeProfitLevel { get; set; }
        [Parameter("Level Multiplier", Group = "TP1 Level Settings", DefaultValue = 1.0)]
        public double FirstTakeProfitLevelMultiplier { get; set; }
        [Parameter("Level Color", Group = "TP1 Level Settings", DefaultValue = "LimeGreen")]
        public string FirstTakeProfitColor { get; set; }

        [Parameter("Draw Level", Group = "TP2 Level Settings", DefaultValue = true)]
        public bool DrawSecondTakeProfitLevel { get; set; }
        [Parameter("Level Multiplier", Group = "TP2 Level Settings", DefaultValue = 2.0)]
        public double SecondTakeProfitLevelMultiplier { get; set; }
        [Parameter("Level Color", Group = "TP2 Level Settings", DefaultValue = "LimeGreen")]
        public string SecondTakeProfitColor { get; set; }

        [Parameter("Draw Level", Group = "TP3 Level Settings", DefaultValue = true)]
        public bool DrawThirdTakeProfitLevel { get; set; }
        [Parameter("Level Multiplier", Group = "TP3 Level Settings", DefaultValue = 3.0)]
        public double ThirdTakeProfitLevelMultiplier { get; set; }
        [Parameter("Level Color", Group = "TP3 Level Settings", DefaultValue = "LimeGreen")]
        public string ThirdTakeProfitColor { get; set; }

        [Output("Signal", LineColor = "Yellow", LineStyle = LineStyle.Solid)]
        public IndicatorDataSeries Signal { get; set; }

        [Output("Baseline", LineColor = "Magenta", LineStyle = LineStyle.Solid)]
        public IndicatorDataSeries Baseline { get; set; }

        private MovingAverage _iSignalMa, _iBaselineMa;
        private Color _buySymbolColor, _sellSymbolColor, _slLevelColor, _tp1LevelColor, _tp2LevelColor, _tp3LevelColor, _entryLevelColor;
        private double _symbolPriceDistance;
        private int _lastEntryIndex = -1;
        private bool _lastTradeTypeWasBuy;

        protected override void Initialize()
        {
            _iSignalMa = Indicators.MovingAverage(SignalMaSource, SignalMaPeriod, SignalMaType);
            _iBaselineMa = Indicators.MovingAverage(BaselineMaSource, BaselineMaPeriod, BaselineMaType);

            _buySymbolColor = Color.FromName(BuySymbolColorName);
            _sellSymbolColor = Color.FromName(SellSymbolColorName);
            _slLevelColor = Color.FromName(StopLossLevelColor);
            _tp1LevelColor = Color.FromName(FirstTakeProfitColor);
            _tp2LevelColor = Color.FromName(SecondTakeProfitColor);
            _tp3LevelColor = Color.FromName(ThirdTakeProfitColor);
            _entryLevelColor = Color.FromName(EntryLevelColor);

            _symbolPriceDistance = PipsToPrice(SymbolDistancePips);
        }

        public override void Calculate(int index)
        {
            Signal[index] = _iSignalMa.Result[index];
            Baseline[index] = _iBaselineMa.Result[index];

            if (Signal.Last(1) > Baseline.Last(1) && Signal.Last(2) < Baseline.Last(2))
            {
                if (UseSymbols)
                    Chart.DrawIcon("Buy Label " + index, BuySymbolType, Bars.OpenTimes.LastValue, Bars.LowPrices.LastValue - _symbolPriceDistance, _buySymbolColor);
                _lastEntryIndex = index;
                _lastTradeTypeWasBuy = true;
            }

            if (Signal.Last(1) < Baseline.Last(1) && Signal.Last(2) > Baseline.Last(2))
            {
                if (UseSymbols)
                    Chart.DrawIcon("Sell Label" + index, SellSymbolType, Bars.OpenTimes.LastValue, Bars.HighPrices.LastValue + _symbolPriceDistance, _sellSymbolColor);
                _lastEntryIndex = index;
                _lastTradeTypeWasBuy = false;
            }
            DrawSlTpLevels(index);
        }

        private double PipsToPrice(double pips)
        {
            return Symbol.PipSize * pips;
        }

        private void DrawSlTpLevels(int currentIndex)
        {
            for (var i = _lastEntryIndex; i <= currentIndex; i++)
            {
                var entryPrice = Bars.OpenPrices[_lastEntryIndex];
                var priceRange = Bars.HighPrices[_lastEntryIndex - 1] - Bars.LowPrices[_lastEntryIndex - 1];
                if (DrawEntryLevel)
                {
                    Chart.DrawTrendLine("Entry " + i, Bars.OpenTimes[i], entryPrice, Bars.OpenTimes[i + 1], entryPrice, _entryLevelColor);
                }
                if (DrawStopLossLevel)
                {
                    var level = (_lastTradeTypeWasBuy) ? entryPrice - StopLossLevelMultiplier * priceRange : entryPrice + StopLossLevelMultiplier * priceRange;
                    Chart.DrawTrendLine("SL " + i, Bars.OpenTimes[i], level, Bars.OpenTimes[i + 1], level, _slLevelColor);
                }
                if (DrawFirstTakeProfitLevel)
                {
                    var level = (_lastTradeTypeWasBuy) ? entryPrice + FirstTakeProfitLevelMultiplier * priceRange : entryPrice - FirstTakeProfitLevelMultiplier * priceRange;
                    Chart.DrawTrendLine("TP1 " + i, Bars.OpenTimes[i], level, Bars.OpenTimes[i + 1], level, _tp1LevelColor);
                }
                if (DrawSecondTakeProfitLevel)
                {
                    var level = (_lastTradeTypeWasBuy) ? entryPrice + SecondTakeProfitLevelMultiplier * priceRange : entryPrice - SecondTakeProfitLevelMultiplier * priceRange;
                    Chart.DrawTrendLine("TP2 " + i, Bars.OpenTimes[i], level, Bars.OpenTimes[i + 1], level, _tp2LevelColor);
                }
                if (DrawThirdTakeProfitLevel)
                {
                    var level = (_lastTradeTypeWasBuy) ? entryPrice + ThirdTakeProfitLevelMultiplier * priceRange : entryPrice - ThirdTakeProfitLevelMultiplier * priceRange;
                    Chart.DrawTrendLine("TP3 " + i, Bars.OpenTimes[i], level, Bars.OpenTimes[i + 1], level, _tp3LevelColor);
                }
            }
        }
    }

}
