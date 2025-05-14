using cAlgo.API;
using AlgorithmicTrading.Position;
using cAlgo.API.Indicators;

namespace AlgorithmicTrading.Strategy.SignalStrategy
{
    public class NnfxSignalStrategySetup
    {
        // Trigger Functions attributes
        private readonly Func<PositionManager, bool> _buyTrigger;
        private readonly Func<PositionManager, bool> _sellTrigger;
        private readonly Func<PositionManager, bool> _exitBuyTrigger;
        private readonly Func<PositionManager, bool> _exitSellTrigger;
        
        // PositionManager attributes
        private readonly double _riskPerTrade;
        private readonly double _stopLossAtrScale;
        
        // Other attributes
        private readonly AverageTrueRange _iAtr;
        private readonly double _pipSize;

        public NnfxSignalStrategySetup(Func<PositionManager, bool> buyTrigger, Func<PositionManager, bool> sellTrigger, 
            Func<PositionManager, bool> exitBuyTrigger, Func<PositionManager, bool> exitSellTrigger, 
            double riskPerTrade, double stopLossAtrScale, AverageTrueRange iAtr, Robot robot)
        {
            _buyTrigger = buyTrigger;
            _sellTrigger = sellTrigger;
            _exitBuyTrigger = exitBuyTrigger;
            _exitSellTrigger = exitSellTrigger;
            
            _riskPerTrade = riskPerTrade;
            _stopLossAtrScale = stopLossAtrScale;

            _iAtr = iAtr;
            _pipSize = robot.Symbol.PipSize;
        }

        public void SetupStrategy(StrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Active Position");

            state1.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            state0.CreateBarTransition("Buy Signal", _buyTrigger, BuyAction, state1);
            state0.CreateBarTransition("Sell Signal", _sellTrigger, SellAction, state1);
            state1.CreateBarTransition("Exit Buy Signal", _exitBuyTrigger, ExitAction, state0);
            state1.CreateBarTransition("Exit Sell Signal", _exitSellTrigger, ExitAction, state0);

            strategy.LoadStrategyState(state0);
        }

        private static bool PositionClosedTrigger(PositionManager position)
        {
            return !position.IsCurrentlyOpened();
        }
        
        private bool BuyAction(PositionManager position)
        {
            return position.OpenPositionDynamic(TradeType.Buy, _riskPerTrade, _stopLossAtrScale * _iAtr.Result.Last(1) / _pipSize);
        }
        
        private bool SellAction(PositionManager position)
        {
            return position.OpenPositionDynamic(TradeType.Sell, _riskPerTrade, _stopLossAtrScale * _iAtr.Result.Last(1) / _pipSize);
        }

        private static bool ExitAction(PositionManager position)
        {
            return position.ClosePositionTotally();
        }
    }
}
