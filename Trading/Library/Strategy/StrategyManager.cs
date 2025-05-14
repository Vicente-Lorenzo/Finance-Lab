using cAlgo.API;
using AlgorithmicTrading.Log;
using AlgorithmicTrading.Position;

namespace AlgorithmicTrading.Strategy
{
    public class StrategyManager
    {
        // Saves a risk management interface and a signal interface
        private readonly List<StrategyInterface> _positionStrategies = new List<StrategyInterface>();
        private readonly List<StrategyInterface> _signalStrategies = new List<StrategyInterface>();
        
        // Save other attributes
        private readonly Robot _robot;
        private readonly Logger _logger;

        // Constructor
        public StrategyManager(Robot robot, Logger logger, bool tickUpdate, bool barUpdate, bool orderUpdate)
        {
            _robot = robot;
            _logger = logger;

            if (tickUpdate) { _robot.Bars.Tick += TickEventUpdateStrategiesCallback; }
            if (barUpdate) { _robot.Bars.BarOpened += BarEventUpdateStrategiesCallback; }
            if (orderUpdate)
            {
                _robot.Positions.Opened += OpenedOrderEventUpdateStrategiesCallback;
                _robot.Positions.Closed += ClosedOrderEventUpdateStrategiesCallback;
            }
        }
        
        // Creates a Position Strategy and adds it to the Update List
        public StrategyInterface CreatePositionStrategyInterface(PositionManager position)
        {
            var strategyInterface = new StrategyInterface("PositionStrategy", position, _robot, _logger);
            _positionStrategies.Add(strategyInterface);
            return strategyInterface;
        }
        
        // Creates a Signal Strategy and adds it to the Update List
        public StrategyInterface CreateSignalStrategyInterface(PositionManager position)
        {
            var strategyInterface = new StrategyInterface("SignalStrategy", position, _robot, _logger);
            _signalStrategies.Add(strategyInterface);
            return strategyInterface;
        }

        // Order Updates every strategy on position/signal lists. If at least one was updated returns true
        private bool OrderUpdatedStrategyStates()
        {
            var control = false;
            foreach (var positionStrategy in _positionStrategies)
                control = control || positionStrategy.OrderUpdateStrategyState();
            foreach (var signalStrategy in _signalStrategies)
                control = control || signalStrategy.OrderUpdateStrategyState();
            return control;
        }
        
        // Tick Updates every strategy on position/signal lists. If at least one was updated returns true
        private bool TickUpdatedStrategyStates()
        {
            var control = false;
            foreach (var positionStrategy in _positionStrategies)
                control = control || positionStrategy.TickUpdateStrategyState();
            foreach (var signalStrategy in _signalStrategies)
                control = control || signalStrategy.TickUpdateStrategyState();
            return control;
        }
        
        // Bar Updates every strategy on position/signal lists. If at least one was updated returns true
        private bool BarUpdatedStrategyStates()
        {
            var control = false;
            foreach (var positionStrategy in _positionStrategies)
                control = control || positionStrategy.BarUpdateStrategyState();
            foreach (var signalStrategy in _signalStrategies)
                control = control || signalStrategy.BarUpdateStrategyState();
            return control;
        }

        // Method called to handle a opened order update. Repeats while no more strategy updates
        private void OpenedOrderEventUpdateStrategiesCallback(PositionOpenedEventArgs args)
        {
            while (OrderUpdatedStrategyStates()) { }
        }
        
        // Method called to handle a closed order update. Repeats while no more strategy updates
        private void ClosedOrderEventUpdateStrategiesCallback(PositionClosedEventArgs args)
        {
            while (OrderUpdatedStrategyStates()) { }
        }
        
        // Method called to handle a tick update. Repeats while no more strategy updates
        private void TickEventUpdateStrategiesCallback(BarsTickEventArgs args)
        {
            while (TickUpdatedStrategyStates()) { }
        }

        // Method called to handle a bar update. Repeats while no more strategy updates
        private void BarEventUpdateStrategiesCallback(BarOpenedEventArgs args)
        {
            while (BarUpdatedStrategyStates()) { }
        }
    }
}