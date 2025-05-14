using AlgorithmicTrading.Position;

namespace AlgorithmicTrading.Strategy.PositionStrategy
{
    public class BasicPositionStrategySetup
    {
        // First Take-Profit attributes
        private readonly bool _useFirstTakeProfit;
        private readonly double _firstTakeProfitPips;
        private readonly double _firstTakeProfitVolumePercentage;
        private readonly bool _useFirstTakeProfitBreakEven;
        
        // Second Take-Profit attributes
        private readonly bool _useSecondTakeProfit;
        private readonly double _secondTakeProfitPips;
        private readonly double _secondTakeProfitVolumePercentage;
        private readonly bool _useSecondTakeProfitBreakEven;
        
        // Third Take-Profit attributes
        private readonly bool _useThirdTakeProfit;
        private readonly double _thirdTakeProfitPips;
        private readonly double _thirdTakeProfitVolumePercentage;
        private readonly bool _useThirdTakeProfitBreakEven;
        
        public BasicPositionStrategySetup(bool useFirstTakeProfit, double firstTakeProfitPips, double firstTakeProfitVolumePercentage, 
            bool useFirstTakeProfitBreakEven, bool useSecondTakeProfit, double secondTakeProfitPips, double secondTakeProfitVolumePercentage, 
            bool useSecondTakeProfitBreakEven, bool useThirdTakeProfit, double thirdTakeProfitPips, double thirdTakeProfitVolumePercentage, 
            bool useThirdTakeProfitBreakEven)
        {
            _useFirstTakeProfit = useFirstTakeProfit;
            _firstTakeProfitPips = firstTakeProfitPips;
            _firstTakeProfitVolumePercentage = firstTakeProfitVolumePercentage;
            _useFirstTakeProfitBreakEven = useFirstTakeProfitBreakEven;
            
            _useSecondTakeProfit = useSecondTakeProfit;
            _secondTakeProfitPips = secondTakeProfitPips;
            _secondTakeProfitVolumePercentage = secondTakeProfitVolumePercentage;
            _useSecondTakeProfitBreakEven = useSecondTakeProfitBreakEven;
            
            _useThirdTakeProfit = useThirdTakeProfit;
            _thirdTakeProfitPips = thirdTakeProfitPips;
            _thirdTakeProfitVolumePercentage = thirdTakeProfitVolumePercentage;
            _useThirdTakeProfitBreakEven = useThirdTakeProfitBreakEven;
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
            return _useFirstTakeProfit && position.Position.Pips >= _firstTakeProfitPips;
        }

        private bool FirstScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_firstTakeProfitVolumePercentage) || (!_useFirstTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool SecondScalingOutTrigger(PositionManager position)
        {
            return _useSecondTakeProfit && position.Position.Pips >= _secondTakeProfitPips;
        }

        private bool SecondScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_secondTakeProfitVolumePercentage) || (!_useSecondTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }

        private bool ThirdScalingOutTrigger(PositionManager position)
        {
            return _useThirdTakeProfit && position.Position.Pips >= _thirdTakeProfitPips;
        }

        private bool ThirdScalingOutAction(PositionManager position)
        {
            return !position.ClosePositionPartially(_thirdTakeProfitVolumePercentage) || (!_useThirdTakeProfitBreakEven) || position.ModifyStopLossToBreakEven(false);
        }
    }
}

/* USEFUL PARAMETERS

[Parameter("Stop-Loss (Pips)", Group = "Stop-Loss Settings", DefaultValue = 20.0, MinValue = 0.1)]
public double StopLossPips { get; set; } 

[Parameter("Enable TP1", Group = "First Take-Profit Settings", DefaultValue = true)]
public bool UseFirstTakeProfit { get; set; }
[Parameter("TP1 (Pips)", Group = "First Take-Profit Settings", DefaultValue = 20.0, MinValue = 0.1)]
public double FirstTakeProfitPips { get; set; }
[Parameter("TP1 Partial Close (%)", Group = "First Take-Profit Settings", DefaultValue = 50, MinValue = 0.1)]
public double FirstTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP1 Break-Even", Group = "First Take-Profit Settings", DefaultValue = true)]
public bool UseFirstTakeProfitBreakEven { get; set; }

[Parameter("Enable TP2", Group = "Second Take-Profit Settings", DefaultValue = true)]
public bool UseSecondTakeProfit { get; set; }
[Parameter("TP2 (Pips)", Group = "Second Take-Profit Settings", DefaultValue = 40.0, MinValue = 0.1)]
public double SecondTakeProfitPips { get; set; }
[Parameter("TP2 Partial Close (%)", Group = "Second Take-Profit Settings", DefaultValue = 30, MinValue = 0.1)]
public double SecondTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP2 Break-Even", Group = "Second Take-Profit Settings", DefaultValue = false)]
public bool UseSecondTakeProfitBreakEven { get; set; }

[Parameter("Enable TP3", Group = "Third Take-Profit Settings", DefaultValue = true)]
public bool UseThirdTakeProfit { get; set; }
[Parameter("TP3 (Pips)", Group = "Third Take-Profit Settings", DefaultValue = 60.0, MinValue = 0.1)]
public double ThirdTakeProfitPips { get; set; }
[Parameter("TP3 Partial Close (%)", Group = "Third Take-Profit Settings", DefaultValue = 20, MinValue = 0.1)]
public double ThirdTakeProfitVolumePercentage { get; set; }
[Parameter("Enable TP3 Break-Even", Group = "Third Take-Profit Settings", DefaultValue = false)]
public bool UseThirdTakeProfitBreakEven { get; set; }

*/
