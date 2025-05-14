using AlgorithmicTrading.Position;

namespace AlgorithmicTrading.Strategy
{
    internal class StrategyTransition
    {
        // Saves the transition attributes
        internal readonly string TransitionName;
        private readonly Func<PositionManager, bool> _trigger;
        private readonly Func<PositionManager, bool> _action;
        internal readonly StrategyState NextState;

        // Constructor
        internal StrategyTransition(string transitionName, Func<PositionManager, bool> trigger, Func<PositionManager, bool> action, StrategyState nextState)
        {
            TransitionName = transitionName;
            _trigger = trigger;
            _action = action;
            NextState = nextState;
        }

        // Returns true if the trigger function returns true
        internal bool ValidateTrigger(PositionManager position) { return _trigger != null && _trigger(position); }

        // Returns true if the action function returns true
        internal bool PerformAction(PositionManager position) { return _action == null || _action(position); }
    }
}