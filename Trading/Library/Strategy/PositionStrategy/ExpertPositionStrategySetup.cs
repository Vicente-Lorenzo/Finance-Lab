using cAlgo.API;
using cAlgo.API.Indicators;
using AlgorithmicTrading.Position;
using AlgorithmicTrading.Utility;
using Calc = AlgorithmicTrading.Utility.MathLibrary;

namespace AlgorithmicTrading.Strategy.PositionStrategy
{
    public class ExpertPositionStrategySetup
    {
        // Stop-Loss attributes
        private readonly bool _useTrailingStop;
        private readonly double _trailingStopAtrScale;
        private readonly double _trailingStopActivationAtrScale;
        private readonly bool _updateTrailingStopOnBar;
        
        // First Take-Profit attributes
        private readonly bool _useFirstTakeProfit;
        private readonly double _firstTakeProfitAtrScale;
        private readonly double _firstTakeProfitVolumePercentage;
        private readonly bool _useFirstTakeProfitBreakEven;
        
        // Second Take-Profit attributes
        private readonly bool _useSecondTakeProfit;
        private readonly double _secondTakeProfitAtrScale;
        private readonly double _secondTakeProfitVolumePercentage;
        private readonly bool _useSecondTakeProfitBreakEven;
        
        // Third Take-Profit attributes
        private readonly bool _useThirdTakeProfit;
        private readonly double _thirdTakeProfitAtrScale;
        private readonly double _thirdTakeProfitVolumePercentage;
        private readonly bool _useThirdTakeProfitBreakEven;
        
        // Anti-Loop attributes
        private double _lastUsedTick;
        private readonly TickManager _tickManager;
        private readonly double _pipSize;
        
        // Atr attributes
        private readonly AverageTrueRange _iAtr;
        
        public ExpertPositionStrategySetup(bool useTrailingStop, double trailingStopAtrScale, double trailingStopActivationAtrScale, 
            bool updateTrailingStopOnBar, bool useFirstTakeProfit, double firstTakeProfitAtrScale, double firstTakeProfitVolumePercentage, 
            bool useFirstTakeProfitBreakEven, bool useSecondTakeProfit, double secondTakeProfitAtrScale, double secondTakeProfitVolumePercentage, 
            bool useSecondTakeProfitBreakEven, bool useThirdTakeProfit, double thirdTakeProfitAtrScale, double thirdTakeProfitVolumePercentage, 
            bool useThirdTakeProfitBreakEven, AverageTrueRange iAtr, TickManager tickManager, Robot robot)
        {
            _useTrailingStop = useTrailingStop;
            _trailingStopAtrScale = trailingStopAtrScale;
            _trailingStopActivationAtrScale = trailingStopActivationAtrScale;
            _updateTrailingStopOnBar = updateTrailingStopOnBar;
            
            _useFirstTakeProfit = useFirstTakeProfit;
            _firstTakeProfitAtrScale = firstTakeProfitAtrScale;
            _firstTakeProfitVolumePercentage = firstTakeProfitVolumePercentage;
            _useFirstTakeProfitBreakEven = useFirstTakeProfitBreakEven;
            
            _useSecondTakeProfit = useSecondTakeProfit;
            _secondTakeProfitAtrScale = secondTakeProfitAtrScale;
            _secondTakeProfitVolumePercentage = secondTakeProfitVolumePercentage;
            _useSecondTakeProfitBreakEven = useSecondTakeProfitBreakEven;
            
            _useThirdTakeProfit = useThirdTakeProfit;
            _thirdTakeProfitAtrScale = thirdTakeProfitAtrScale;
            _thirdTakeProfitVolumePercentage = thirdTakeProfitVolumePercentage;
            _useThirdTakeProfitBreakEven = useThirdTakeProfitBreakEven;

            _tickManager = tickManager;
            _pipSize = robot.Symbol.PipSize;

            _iAtr = iAtr;
        }
        
        public void SetupStrategy(StrategyInterface strategy)
        {
            var state0 = strategy.CreateStrategyState("No Position");
            var state1 = strategy.CreateStrategyState("Waiting TP1");
            var state2 = strategy.CreateStrategyState("Waiting TP2");
            var state3 = strategy.CreateStrategyState("Waiting TP3");
            var state4 = strategy.CreateStrategyState("Waiting Close");

            state0.CreateTickTransition("Position Opened", PositionOpenedTrigger, null, state1);
            state0.CreateBarTransition("Position Opened", PositionOpenedTrigger, null, state1);

            state1.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state1.CreateTickTransition("Position Hit TP1", FirstScalingOutTrigger, FirstScalingOutAction, state2);
            state1.CreateBarTransition("Position Hit TP1", FirstScalingOutTrigger, FirstScalingOutAction, state2);
            
            state2.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state2.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state2.CreateTickTransition("Position Hit TP2", SecondScalingOutTrigger, SecondScalingOutAction, state3);
            state2.CreateBarTransition("Position Hit TP2", SecondScalingOutTrigger, SecondScalingOutAction, state3);
            
            state3.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state3.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);
            state3.CreateTickTransition("Position Hit TP3", ThirdScalingOutTrigger, ThirdScalingOutAction, state4);
            state3.CreateBarTransition("Position Hit TP3", ThirdScalingOutTrigger, ThirdScalingOutAction, state4);
            
            state4.CreateTickTransition("Position Closed", PositionClosedTrigger, null, state0);
            state4.CreateBarTransition("Position Closed", PositionClosedTrigger, null, state0);

            if (_updateTrailingStopOnBar)
            {
                state1.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state1);
                state2.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state2);
                state3.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state3);
                state4.CreateBarTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state4);
            }
            else
            {
                state1.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state1);
                state2.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state2);
                state3.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state3);
                state4.CreateTickTransition("Update Trailing-Stop", UpdateTrailingStopTrigger, UpdateTrailingStopAction, state4);
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

        private bool FirstScalingOutTrigger(PositionManager position)
        {
            return _useFirstTakeProfit && position.Position.Pips >= _firstTakeProfitAtrScale * _iAtr.Result.Last(1) / _pipSize;
        }

        private bool FirstScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_firstTakeProfitVolumePercentage) || (!_useFirstTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool SecondScalingOutTrigger(PositionManager position)
        {
            return _useSecondTakeProfit && position.Position.Pips >= _secondTakeProfitAtrScale * _iAtr.Result.Last(1) / _pipSize;
        }

        private bool SecondScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_secondTakeProfitVolumePercentage) || (!_useSecondTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool ThirdScalingOutTrigger(PositionManager position)
        {
            return _useThirdTakeProfit && position.Position.Pips >= _thirdTakeProfitAtrScale * _iAtr.Result.Last(1) / _pipSize;
        }

        private bool ThirdScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_thirdTakeProfitVolumePercentage) || (!_useThirdTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }
        
        private bool UpdateTrailingStopTrigger(PositionManager position)
        {
            return _useTrailingStop && Math.Abs(_lastUsedTick - _tickManager.TickCount) > double.Epsilon 
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

/* USEFUL PARAMETERS
 
[Parameter("ATR Period", Group = "Position Scaling ATR Settings", DefaultValue = 14, MinValue = 1)]
public int PositionATRPeriod { get; set; }
[Parameter("ATR Ma Type", Group = "Position Scaling ATR Settings", DefaultValue = MovingAverageType.Simple)]
public MovingAverageType PositionATRMaType { get; set; }

[Parameter("Stop-Loss (xATR)", Group = "Stop-Loss Settings", DefaultValue = 1.5, MinValue = 0.1)]
public double StopLossAtrScale { get; set; }
[Parameter("Use Trailing-Stop", Group = "Stop-Loss Settings", DefaultValue = true)]
public bool UseTrailingStop { get; set; }
[Parameter("Trailing-Stop (xATR)", Group = "Stop-Loss Settings", DefaultValue = 1.5, MinValue = 0.1)]
public double TrailingStopAtrScale { get; set; }
[Parameter("Trailing-Stop Activation (xATR)", Group = "Stop-Loss Settings", DefaultValue = 1.0, MinValue = 0.1)]
public double TrailingStopActivationAtrScale { get; set; }
[Parameter("Update Trailing-Stop On Bar", Group = "Stop-Loss Settings", DefaultValue = false)]
public bool UpdateTrailingStopOnBar { get; set; }

[Parameter("Enable TP1", Group = "First Take-Profit Settings", DefaultValue = true)]
public bool UseFirstTakeProfit { get; set; }
[Parameter("TP1 (xATR)", Group = "First Take-Profit Settings", DefaultValue = 1.0, MinValue = 0.1)]
public double FirstTakeProfitAtrScale { get; set; }
[Parameter("TP1 Partial Close (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
public double FirstTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP1 Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
public bool UseFirstTakeProfitBreakEven { get; set; }

[Parameter("Enable TP2", Group = "Second Take-Profit Settings", DefaultValue = true)]
public bool UseSecondTakeProfit { get; set; }
[Parameter("TP2 (xATR)", Group = "Second Take-Profit Settings", DefaultValue = 1.5, MinValue = 0.1)]
public double SecondTakeProfitAtrScale { get; set; }
[Parameter("TP2 Partial Close (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
public double SecondTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP2 Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
public bool UseSecondTakeProfitBreakEven { get; set; }

[Parameter("Enable TP3", Group = "Third Take-Profit Settings", DefaultValue = true)]
public bool UseThirdTakeProfit { get; set; }
[Parameter("TP3 (xATR)", Group = "Third Take-Profit Settings", DefaultValue = 2.0, MinValue = 0.1)]
public double ThirdTakeProfitAtrScale { get; set; }
[Parameter("TP3 Partial Close (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
public double ThirdTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP3 Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
public bool UseThirdTakeProfitBreakEven { get; set; }

*/
