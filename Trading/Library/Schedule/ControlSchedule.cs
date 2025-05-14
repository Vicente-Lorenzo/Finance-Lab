using cAlgo.API;

namespace AlgorithmicTrading.Schedule
{
    public class ControlSchedule
    {
        // Trades attributes
        private DateTime _mostRecentTime;
        private int _dailyOpenedTrades;
        private readonly int _maxTradesAtOnce;
        private readonly int _maxTradesPerDay;
        private readonly string _managerIdLabel;
        
        // Other attributes
        private readonly Robot _robot;
        
        public ControlSchedule(int maxTradesAtOnce, int maxTradesPerDay, string managerIdLabel, Robot robot)
        {
            _maxTradesAtOnce = maxTradesAtOnce;
            _maxTradesPerDay = maxTradesPerDay;
            _managerIdLabel = managerIdLabel;
            _robot = robot;

            _dailyOpenedTrades = 0;
            _mostRecentTime = _robot.Time;
            
            _robot.Positions.Opened += IncrementOpenedPositions;
        }

        private void IncrementOpenedPositions(PositionOpenedEventArgs args)
        {
            var openedLabel = args.Position.Label;
            if (_managerIdLabel != null && (openedLabel == null || !openedLabel.Contains(_managerIdLabel)))
                return;
            _dailyOpenedTrades++;            
        }

        public bool IsOnSchedule()
        {
            if (_robot.Time.Date != _mostRecentTime.Date)
            {
                _mostRecentTime = _robot.Time;
                _dailyOpenedTrades = 0;
            }
            return _robot.Positions.Count < _maxTradesAtOnce && _dailyOpenedTrades < _maxTradesPerDay;
        }
    }
}