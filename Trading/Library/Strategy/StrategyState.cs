using AlgorithmicTrading.Position;

namespace AlgorithmicTrading.Strategy
{
    public class StrategyState
    {
        // Saves the State attributes
        internal readonly string StateName;
        private readonly List<StrategyTransition> _orderTransitions = new List<StrategyTransition>();
        private readonly List<StrategyTransition> _tickTransitions = new List<StrategyTransition>();
        private readonly List<StrategyTransition> _barTransitions = new List<StrategyTransition>();

        public StrategyState(string stateName) { StateName = stateName; }

        // Creates a new order transition and adds it to the list
        public void CreateOrderTransition(string transitionName, Func<PositionManager, bool> trigger, Func<PositionManager, bool> action, StrategyState nextState)
        {
            _orderTransitions.Add(new StrategyTransition(transitionName, trigger, action, nextState));
        }
        
        // Creates a new tick transition and adds it to the list
        public void CreateTickTransition(string transitionName, Func<PositionManager, bool> trigger, Func<PositionManager, bool> action, StrategyState nextState)
        {
            _tickTransitions.Add(new StrategyTransition(transitionName, trigger, action, nextState));
        }

        // Crates a new bar transition and adds it to the list
        public void CreateBarTransition(string transitionName, Func<PositionManager, bool> trigger, Func<PositionManager, bool> action, StrategyState nextState)
        {
            _barTransitions.Add(new StrategyTransition(transitionName, trigger, action, nextState));
        }
        
        // Auxiliary method to validate a list of transitions and return a valid one. Returns null if none is found
        private static StrategyTransition GetValidTransition(List<StrategyTransition> transitionList, PositionManager position)
        {
            foreach (var transition in transitionList)
                if (transition.ValidateTrigger(position))
                    return transition;
            return null;
        }
        
        // Returns the first valid transition in the order list. Returns null if none is found
        internal StrategyTransition GetValidOrderTransition(PositionManager position) { return GetValidTransition(_orderTransitions, position); }
        
        // Returns the first valid transition in the tick list. Returns null if none is found
        internal StrategyTransition GetValidTickTransition(PositionManager position) { return GetValidTransition(_tickTransitions, position); }

        // Returns the first valid transition in the bar list. Returns null if none is found
        internal StrategyTransition GetValidBarTransition(PositionManager position) { return GetValidTransition(_barTransitions, position); }
    }
}