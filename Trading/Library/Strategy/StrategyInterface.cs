using cAlgo.API;
using AlgorithmicTrading.Log;
using AlgorithmicTrading.Position;
using AlgorithmicTrading.Utility;

namespace AlgorithmicTrading.Strategy
{
    public class StrategyInterface
    {
        // Saves the record file path 
        private readonly string _recordFilePath;
        
        // Saves the Strategy Interface attributes
        private StrategyState _currentState;
        private readonly List<StrategyState> _possibleStates = new List<StrategyState>();
        private readonly PositionManager _associatedPosition;

        // Saves other attributes
        private readonly Robot _robot;
        private readonly SpecificLogger _logger;

        // Constructor
        public StrategyInterface(string strategyName, PositionManager associatedPosition, Robot robot, Logger logger)
        {
            _associatedPosition = associatedPosition;
            
            _robot = robot;
            _logger = new SpecificLogger(logger, strategyName, associatedPosition.ManagerId);

            _recordFilePath = FileManager.BuildRecordFileName(_robot.Symbol, _robot.TimeFrame, strategyName);
        }

        // Creates a new strategy state and adds it to the list
        public StrategyState CreateStrategyState(string stateName)
        {
            var state = new StrategyState(stateName);
            _possibleStates.Add(state);
            return state;
        }
        
        // Method to save the current strategy state in the record if it was changed and if it is not a backtest
        public void SaveStrategyState(StrategyState newState)
        {
            // If the state was not changed returns
            if (_currentState.Equals(newState))
                return;
            
            // If the code gets here the state was changed, therefore, updates it
            _currentState = newState;
            
            // If it is not a realtime execution does not save the state on the record folder 
            if (_robot.RunningMode != RunningMode.RealTime) 
                return;

            // If the code gets here it is a realtime execution, therefore, saves the state name in the record
            FileManager.SaveStringToFile(_recordFilePath,_currentState.StateName);
            _logger.Debug($"Saved strategy state with name \"{_currentState.StateName}\" to the record folder");
        }

        // Method to load the current strategy state from the record if it is not a backtest
        public void LoadStrategyState(StrategyState defaultState)
        {
            // Overrides the current state with the default state
            _currentState = defaultState;

            // If it is not a realtime execution returns
            if (_robot.RunningMode != RunningMode.RealTime) 
                return;
            
            // If the code gets here it is a realtime execution so it must try to load a state name from the record
            var loadedStateName = FileManager.LoadStringFromFile(_recordFilePath);
            
            // If no record file was found saves the current state and returns
            if (loadedStateName == null)
            {
                FileManager.SaveStringToFile(_recordFilePath, _currentState.StateName);
                return;
            }
            
            // If the code gets here a loaded state was found. Tries to find a state with the loaded state name
            foreach (var state in _possibleStates)
            {
                if (state.StateName.Equals(loadedStateName))
                {
                    _currentState = state;
                    _logger.Debug($"Loaded strategy state \"{_currentState.StateName}\" from the record folder");
                    return;
                }
            }
            
            // If the code gets here than no strategy state is equal to the loaded one, therefore saves the default state
            FileManager.SaveStringToFile(_recordFilePath, _currentState.StateName);
        }

        // Auxiliary method that performs the action and saves the state
        private bool UpdateStrategyState(StrategyTransition transition)
        {
            // If there is not transition to be made returns false
            if (transition == null) 
                return false;
            
            // If the code gets here there is a transition to be made, therefore tries to perform it
            if (!transition.PerformAction(_associatedPosition))
            {
                _logger.Error("Unable to update the strategy state because an error occurred performing the action");
                return false;
            }
            _logger.Debug($"Updated strategy state from \"{_currentState.StateName}\" to \"{transition.NextState.StateName}\" because \"{transition.TransitionName}\"");
            SaveStrategyState(transition.NextState);
            return true;
        }
        
        // Tries to find a possible order transition. If finds one, calls the auxiliary method
        public bool OrderUpdateStrategyState() { return UpdateStrategyState(_currentState.GetValidOrderTransition(_associatedPosition)); }
        
        // Tries to find a possible tick transition. If finds one, calls the auxiliary method
        public bool TickUpdateStrategyState() { return UpdateStrategyState(_currentState.GetValidTickTransition(_associatedPosition)); }

        // Tries to find a possible bar transition. If finds one, calls the auxiliary method
        public bool BarUpdateStrategyState() { return UpdateStrategyState(_currentState.GetValidBarTransition(_associatedPosition)); }
    }
}