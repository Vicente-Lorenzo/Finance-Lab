using cAlgo.API;
using AlgorithmicTrading.Position;

namespace AlgorithmicTrading.Strategy.SignalStrategy
{
    public class BasicSignalStrategySetup
    {
        // Control attributes
        private readonly bool _searchOnBar;
        
        // Trigger Functions attributes
        private readonly Func<PositionManager, bool> _buyTrigger;
        private readonly Func<PositionManager, bool> _sellTrigger;
        private readonly Func<PositionManager, bool> _exitBuyTrigger;
        private readonly Func<PositionManager, bool> _exitSellTrigger;
        
        // PositionManager attributes
        private readonly double _staticVolumeLots;
        private readonly bool _useDynamicVolume;
        private readonly double _dynamicVolumePercentage;
        private readonly double _stopLossPips;
        
        // Other attributes
        private readonly Robot _robot;

        public BasicSignalStrategySetup(bool searchOnBar, Func<PositionManager, bool> buyTrigger, Func<PositionManager, bool> sellTrigger, 
            Func<PositionManager, bool> exitBuyTrigger, Func<PositionManager, bool> exitSellTrigger, double staticVolumeLots, bool useDynamicVolume, 
            double dynamicVolumePercentage, double stopLossPips, Robot robot)
        {
            _searchOnBar = searchOnBar;
            
            _buyTrigger = buyTrigger;
            _sellTrigger = sellTrigger;
            _exitBuyTrigger = exitBuyTrigger;
            _exitSellTrigger = exitSellTrigger;
            
            _staticVolumeLots = staticVolumeLots;
            _useDynamicVolume = useDynamicVolume;
            _dynamicVolumePercentage = dynamicVolumePercentage;
            _stopLossPips = stopLossPips;
            _robot = robot;
        }

        public void SetupStrategy(StrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Active Position");

            state1.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            if (_searchOnBar)
            {
                state0.CreateBarTransition("Buy Signal", _buyTrigger, BuyAction, state1);
                state0.CreateBarTransition("Sell Signal", _sellTrigger, SellAction, state1);
                state1.CreateBarTransition("Exit Buy Signal", _exitBuyTrigger, ExitAction, state0);
                state1.CreateBarTransition("Exit Sell Signal", _exitSellTrigger, ExitAction, state0);
            }
            else
            {
                state0.CreateTickTransition("Buy Signal", _buyTrigger, BuyAction, state1);
                state0.CreateTickTransition("Sell Signal", _sellTrigger, SellAction, state1);
                state1.CreateTickTransition("Exit Buy Signal", _exitBuyTrigger, ExitAction, state0);
                state1.CreateTickTransition("Exit Sell Signal", _exitSellTrigger, ExitAction, state0);
            }

            strategy.LoadStrategyState(state0);
        }

        private static bool PositionClosedTrigger(PositionManager position)
        {
            return !position.IsCurrentlyOpened();
        }
        
        private bool BuyAction(PositionManager position)
        {
            return _useDynamicVolume ? 
                position.OpenPositionDynamic(TradeType.Buy, _dynamicVolumePercentage, _stopLossPips) : 
                position.OpenPositionStatic(TradeType.Buy, _robot.Symbol.QuantityToVolumeInUnits(_staticVolumeLots), _stopLossPips);
        }
        
        private bool SellAction(PositionManager position)
        {
            return _useDynamicVolume ? 
                position.OpenPositionDynamic(TradeType.Sell, _dynamicVolumePercentage, _stopLossPips) : 
                position.OpenPositionStatic(TradeType.Sell, _robot.Symbol.QuantityToVolumeInUnits(_staticVolumeLots), _stopLossPips);
        }

        private static bool ExitAction(PositionManager position)
        {
            return position.ClosePositionTotally();
        }
    }
}

/* USEFUL PARAMETERS

[Parameter("Fixed Volume (Lots)", Group = "Volume Settings", DefaultValue = 0.1, MinValue = 0.01)]
public double FixedVolumeLots { get; set; }
[Parameter("Use Dynamic Volume", Group = "Volume Settings", DefaultValue = true)]
public bool UseDynamicVolume { get; set; }
[Parameter("Dynamic Volume (%)", Group = "Volume Settings", DefaultValue = 2.0, MinValue = 0.1)]
public double DynamicVolumePercentage { get; set; }

*/