using System;
using cAlgo.API;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = true, AccessRights = AccessRights.None)]
    public class ZigZagClose : Indicator
    {
        [Parameter("Depth", Group = "Indicator Settings", DefaultValue = 12)]
        public int Depth { get; set; }
        [Parameter("Deviation", Group = "Indicator Settings", DefaultValue = 5)]
        public int Deviation { get; set; }
        [Parameter("BackStep", Group = "Indicator Settings", DefaultValue = 3)]
        public int BackStep { get; set; }

        [Output("Zig Zag", LineColor = "Yellow")]
        public IndicatorDataSeries ZigZagResult { get; set; }

        private int _lastHighIndex, _lastLowIndex, _whatLookFor;
        private double _high, _low, _lastHigh, _lastLow, _currentLow, _currentHigh;

        private IndicatorDataSeries _auxLowValues;
        private IndicatorDataSeries _auxHighValues;

        protected override void Initialize()
        {
            _auxLowValues = CreateDataSeries();
            _auxHighValues = CreateDataSeries();
        }

        public override void Calculate(int index)
        {
            _currentLow = Bars.ClosePrices.Minimum(Depth);
            if (Math.Abs(_currentLow - _lastLow) < double.Epsilon)
                _currentLow = 0.0;
            else
            {
                _lastLow = _currentLow;
                if (Bars.ClosePrices[index] - _currentLow > Deviation * Symbol.TickSize)
                    _currentLow = 0.0;
                else
                    for (var i = 1; i <= BackStep; i++)
                        if (Math.Abs(_auxLowValues[index - i]) > double.Epsilon && _auxLowValues[index - i] > _currentLow)
                            _auxLowValues[index - i] = 0.0;
            }
            if (Math.Abs(Bars.ClosePrices[index] - _currentLow) < double.Epsilon)
                _auxLowValues[index] = _currentLow;
            else
                _auxLowValues[index] = 0.0;

            _currentHigh = Bars.ClosePrices.Maximum(Depth);
            if (Math.Abs(_currentHigh - _lastHigh) < double.Epsilon)
                _currentHigh = 0.0;
            else
            {
                _lastHigh = _currentHigh;
                if (_currentHigh - Bars.ClosePrices[index] > Deviation * Symbol.TickSize)
                    _currentHigh = 0.0;
                else
                    for (var i = 1; i <= BackStep; i++)
                        if (Math.Abs(_auxHighValues[index - i]) > double.Epsilon && _auxHighValues[index - i] < _currentHigh)
                            _auxHighValues[index - i] = 0.0;
            }

            if (Math.Abs(Bars.ClosePrices[index] - _currentHigh) < double.Epsilon)
                _auxHighValues[index] = _currentHigh;
            else
                _auxHighValues[index] = 0.0;

            switch (_whatLookFor)
            {
                case 0:
                    if (Math.Abs(_low - 0) < double.Epsilon && Math.Abs(_high - 0) < double.Epsilon)
                    {
                        if (Math.Abs(_auxHighValues[index]) > double.Epsilon)
                        {
                            _high = Bars.ClosePrices[index];
                            _lastHighIndex = index;
                            _whatLookFor = -1;
                            ZigZagResult[index] = _high;
                        }
                        if (Math.Abs(_auxLowValues[index]) > double.Epsilon)
                        {
                            _low = Bars.ClosePrices[index];
                            _lastLowIndex = index;
                            _whatLookFor = 1;
                            ZigZagResult[index] = _low;
                        }
                    }
                    break;
                case 1:
                    if (Math.Abs(_auxLowValues[index]) > double.Epsilon && _auxLowValues[index] < _low && Math.Abs(_auxHighValues[index] - 0.0) < double.Epsilon)
                    {
                        ZigZagResult[_lastLowIndex] = double.NaN;
                        _lastLowIndex = index;
                        _low = _auxLowValues[index];
                        ZigZagResult[index] = _low;
                    }
                    if (Math.Abs(_auxHighValues[index] - 0.0) > double.Epsilon && Math.Abs(_auxLowValues[index] - 0.0) < double.Epsilon)
                    {
                        _high = _auxHighValues[index];
                        _lastHighIndex = index;
                        ZigZagResult[index] = _high;
                        _whatLookFor = -1;
                    }
                    break;
                case -1:
                    if (Math.Abs(_auxHighValues[index]) > double.Epsilon && _auxHighValues[index] > _high && Math.Abs(_auxLowValues[index] - 0.0) < double.Epsilon)
                    {
                        ZigZagResult[_lastHighIndex] = double.NaN;
                        _lastHighIndex = index;
                        _high = _auxHighValues[index];
                        ZigZagResult[index] = _high;
                    }
                    if (Math.Abs(_auxLowValues[index]) > double.Epsilon && Math.Abs(_auxHighValues[index]) <= double.Epsilon)
                    {
                        _low = _auxLowValues[index];
                        _lastLowIndex = index;
                        ZigZagResult[index] = _low;
                        _whatLookFor = 1;
                    }
                    break;
                default:
                    return;
            }
        }
    }
}
