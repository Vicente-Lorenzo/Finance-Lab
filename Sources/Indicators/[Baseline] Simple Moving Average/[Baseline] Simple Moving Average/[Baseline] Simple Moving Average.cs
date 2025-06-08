using System;
using cAlgo.API;
using cAlgo.API.Collections;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo
{
    [Indicator(AccessRights = AccessRights.None)]
    public class BaselineSimpleMovingAverage : Indicator
    {
        [Output("Result")]
        public IndicatorDataSeries Result { get; set; }

        protected override void Initialize()
        {
            
        }

        public override void Calculate(int index)
        {
            
        }
    }
}