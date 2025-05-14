using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Position;
using AlgorithmicTrading.Utility;
using Calc = AlgorithmicTrading.Utility.MathLibrary;

namespace AlgorithmicTrading.Strategy.PositionStrategy
{
    public class NnfxPositionStrategySetup
    {
        // Stop-Loss attributes
        private readonly double _trailingStopAtrScale;
        private readonly double _trailingStopActivationAtrScale;
        private readonly bool _updateTrailingStopOnBar;
        
        // First Take-Profit attributes
        private readonly double _takeProfitAtrScale;
        private readonly double _takeProfitVolumePercentage;
        
        // Anti-Loop attributes
        private double _lastUsedTick;
        private readonly TickManager _tickManager;
        private readonly double _pipSize;
        
        // Atr attributes
        private readonly AverageTrueRange _iAtr;
        
        public NnfxPositionStrategySetup(double trailingStopAtrScale, double trailingStopActivationAtrScale, 
            bool updateTrailingStopOnBar, double takeProfitAtrScale, double takeProfitVolumePercentage, 
            AverageTrueRange iAtr, TickManager tickManager, Robot robot)
        {
            _trailingStopAtrScale = trailingStopAtrScale;
            _trailingStopActivationAtrScale = trailingStopActivationAtrScale;
            _updateTrailingStopOnBar = updateTrailingStopOnBar;
            
            _takeProfitAtrScale = takeProfitAtrScale;
            _takeProfitVolumePercentage = takeProfitVolumePercentage;
            
            _tickManager = tickManager;
            _pipSize = robot.Symbol.PipSize;

            _iAtr = iAtr;
        }
        
        public void SetupStrategy(StrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Waiting TP");
            var state2 = strategy.CreateStrategyState("Waiting Close");

            state0.CreateTickTransition("Position Opened", PositionOpenedTrigger, null, state1);
            state0.CreateBarTransition("Position Opened", PositionOpenedTrigger, null, state1);

            state1.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateTickTransition("Position Hit TP", ScalingOutTrigger, ScalingOutAction, state2);
            state1.CreateBarTransition("Position Hit TP", ScalingOutTrigger, ScalingOutAction, state2);
            
            state2.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state2.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            if (_updateTrailingStopOnBar)
            {
                state1.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state1);
                state2.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state2);
            }
            else
            {
                state1.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state1);
                state2.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state2);
            }
            
            strategy.LoadStrategyState(state0);
        }
        
        private static bool PositionOpenedTrigger(PositionManager position)
        {
            return position.IsCurrentlyOpened();
        }

        private static bool PositionClosedTrigger(PositionManager position)
        {
            return !position.IsCurrentlyOpened();
        }

        private bool ScalingOutTrigger(PositionManager position)
        {
            return position.Position.Pips >= _takeProfitAtrScale * _iAtr.Result.Last(1) / _pipSize;
        }

        private bool ScalingOutAction(PositionManager position)
        {
            return position.ClosePositionPartially(_takeProfitVolumePercentage) && position.ModifyStopLossToBreakEven(true);
        }

        private bool UpdateTrailingStopTrigger(PositionManager position)
        {
            return Math.Abs(_lastUsedTick - _tickManager.TickCount) > double.Epsilon 
                && position.Position.Pips >= _trailingStopActivationAtrScale * _iAtr.Result.Last(1) / _pipSize
                && position.Position.Pips - _trailingStopAtrScale * _iAtr.Result.Last(1) / _pipSize > Calc.CalculateStopLossPips(position.Position, _pipSize);
        }

        private bool UpdateTrailingStopAction(PositionManager position)
        {
            _lastUsedTick = _tickManager.TickCount;
            return position.ModifyCurrentStopLoss(_trailingStopAtrScale * _iAtr.Result.Last(1) / _pipSize);
        }
    }
}
