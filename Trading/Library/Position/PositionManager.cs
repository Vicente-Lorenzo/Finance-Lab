using cAlgo.API;
using cAlgo.API.Internals;
using AlgorithmicTrading.Log;
using AlgorithmicTrading.Utility;

namespace AlgorithmicTrading.Position
{
    public class PositionManager
    {
        // Position Attributes
        public cAlgo.API.Position? Position;
        private double _positionTotalVolume;

        // Manager constant label Attributes
        public readonly string ManagerId;
        public readonly string ManagerGroupLabel;
        
        // Correlation constant label Attributes
        private readonly string _uniquePositionLabel;

        // Modified Event Attributes
        private readonly Queue<cAlgo.API.Position> _modifiedStopLossQueue;
        private readonly Queue<cAlgo.API.Position> _modifiedTakeProfitQueue;
        private readonly Queue<cAlgo.API.Position> _modifiedVolumeQueue;
        private readonly Queue<double> _totalVolumeQueue;
        
        // Other Attributes
        private readonly Robot _robot;
        private readonly Symbol _symbol;
        private readonly SpecificLogger _logger;

        public PositionManager(string managerId, string statisticsId, Robot robot, Logger logger)
        {
            // Initializes the unique manager labels
            ManagerId = managerId;
            ManagerGroupLabel = LabelManager.BuildManagerGroupLabel(managerId, robot.Symbol.Name, robot.TimeFrame.Name);

            // Initializes the Positions Unique label
            _uniquePositionLabel = LabelManager.BuildUniqueLabel(managerId, robot.Symbol.Name, robot.TimeFrame.Name, statisticsId);

            // Saves the other attributes
            _robot = robot;
            _symbol = _robot.Symbol;
            _logger = new SpecificLogger(logger, "PositionManager", managerId);

            // Subscribes to the position event callbacks
            _robot.Positions.Opened += PositionOpenedEventCallback;
            _robot.Positions.Closed += PositionClosedEventCallback;
            _robot.Positions.Modified += PositionModifiedEventCallback;

            // Creates the queues
            _modifiedStopLossQueue = new Queue<cAlgo.API.Position>();
            _modifiedTakeProfitQueue = new Queue<cAlgo.API.Position>();
            _modifiedVolumeQueue = new Queue<cAlgo.API.Position>();
            _totalVolumeQueue = new Queue<double>();

            // Initialize the position pointer
            InitializePositionAttributes();
        }
        
        // Initialize the position after cold start
        private void InitializePositionAttributes() 
        {
            var positions = _robot.Positions.Where(pos => pos.Label.Contains(ManagerGroupLabel)).ToArray();
            if (positions.Length == 0)
                Position = null;
            else if (positions.Length == 1)
                Position = positions[0];
            else
                throw new Exception("Detected two or more positions opened with the same unique manager id");
        }

        // Returns true if the position is opened
        public bool IsCurrentlyOpened()
        {
            // If there is no position saved returns false
            if (Position == null)
                return false;
            // If there is a position saved and it is currently opened returns true
            if (_robot.Positions.Contains<cAlgo.API.Position>(Position))
                return true;
            // If the code gets here it means the position hit a stop limit
            Position = null;
            return false;
        }

        // Auxiliary method to open a market position
        private bool OpenPositionAux(TradeType tradeType, double volumeToOpen, double? slPips, double? tpPips)
        {
            if (IsCurrentlyOpened())
            {
                _logger.Warning("Unable to open position because it is already opened");
                return true;
            }

            if (volumeToOpen < _symbol.VolumeInUnitsMin)
            {
                _logger.Error($"Unable to open new position because {volumeToOpen} units is invalid volume");
                return false;
            }

            volumeToOpen = _symbol.NormalizeVolumeInUnits(volumeToOpen, RoundingMode.Down);
            var res = _robot.ExecuteMarketOrder(tradeType, _symbol.Name, volumeToOpen, _uniquePositionLabel, slPips, tpPips);
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to open position because an error occurred: {res.Error}");
                return false;
            }

            // Saves the position pointer
            Position = res.Position;
            _positionTotalVolume = Position.VolumeInUnits;
            return true;
        }

        // Method to open a normal position by specifying the volume to open
        public bool OpenPositionStatic(TradeType tradeType, double volumeToOpen, double? slPips = null, double? tpPips = null)
        {
            return OpenPositionAux(tradeType, volumeToOpen, slPips, tpPips);
        }

        // Method to open a position like a pro providing the risk per trade
        public bool OpenPositionDynamic(TradeType tradeType, double riskPercentage, double slPips, double? tpPips = null)
        {
            if (riskPercentage < 0 || riskPercentage > 100)
            {
                _logger.Error($"Unable to open new position because {riskPercentage}% is an invalid risk");
                return false;
            }

            var volume = MathLibrary.CalculateVolumeByRisk(riskPercentage, slPips, _robot.Account.Balance, _symbol.PipValue);
            return OpenPositionAux(tradeType, volume, slPips, tpPips);
        }

        // Auxiliary method to close a market position
        private bool ClosePositionAux(double volumeToClose)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to close position because it is already closed");
                return true;
            }

            if (volumeToClose <= 0)
            {
                _logger.Error($"Unable to close position because {volumeToClose} units is invalid");
                return false;
            }

            volumeToClose = _symbol.NormalizeVolumeInUnits(volumeToClose, RoundingMode.Up);
            // Close position totally
            if (volumeToClose >= Position.VolumeInUnits)
            {
                var res = _robot.ClosePosition(Position, Position.VolumeInUnits);
                if (!res.IsSuccessful)
                {
                    _logger.Error($"Unable to close position totally because an error occured: {res.Error}");
                    return false;
                }

                // Deletes the position pointer since it is no longer opened
                Position = null;
                _totalVolumeQueue.Enqueue(_positionTotalVolume);
            }
            // Close position partially
            else
            {
                var res = _robot.ClosePosition(Position, volumeToClose);
                if (!res.IsSuccessful)
                {
                    _logger.Error($"Unable to close position partially because an error occured: {res.Error}");
                    return false;
                }

                // Adds the modification of the volume to the callback queue
                _modifiedVolumeQueue.Enqueue(Position);
                _totalVolumeQueue.Enqueue(_positionTotalVolume);
            }
            return true;
        }

        // Method to close the position totally
        public bool ClosePositionTotally()
        {
            return ClosePositionAux(_positionTotalVolume);
        }

        // Method to close the position partially
        public bool ClosePositionPartially(double volumePercentage)
        {
            if (volumePercentage < 0 || volumePercentage > 100)
            {
                _logger.Error($"Unable to close position because {volumePercentage}% is an invalid percentage");
                return false;
            }
            return ClosePositionAux(MathLibrary.CalculateVolumeByPercentage(volumePercentage, _positionTotalVolume));
        }

        // Method to modify the entry stop-loss of the position
        public bool ModifyEntryStopLoss(double slPips)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to modify position entry stop-loss because it is not opened");
                return true;
            }

            var res = Position.ModifyStopLossPips(slPips);
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to modify position entry stop-loss because an error occured: {res.Error}");
                return false;
            }

            // Adds the modification of the stop-loss to the callback queue
            _modifiedStopLossQueue.Enqueue(Position);
            return true;
        }

        // Method to modify the current stop-loss of the position
        public bool ModifyCurrentStopLoss(double slPips)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to modify position current stop-loss because it is not opened");
                return true;
            }

            var res = Position.TradeType == TradeType.Buy ?
                Position.ModifyStopLossPrice(_symbol.Ask - MathLibrary.ConvertPipsToDeltaPrice(slPips, _symbol.PipSize)) :
                Position.ModifyStopLossPrice(_symbol.Bid + MathLibrary.ConvertPipsToDeltaPrice(slPips, _symbol.PipSize));
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to modify position current stop-loss because an error occured: {res.Error}");
                return false;
            }

            // Adds the modification of the stop-loss to the callback queue
            _modifiedStopLossQueue.Enqueue(Position);
            return true;
        }

        // Method to modify the stop-loss to break-even of the position
        public bool ModifyStopLossToBreakEven(bool spreadCoverage, double extraPips = 0.0)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to modify position stop-loss to break-even because it is not opened");
                return true;
            }

            if (extraPips < 0)
            {
                _logger.Warning("Unable to modify position stop-loss to breakeven because extra pips are negative");
                return true;
            }

            var extraPrice = spreadCoverage ? 
                MathLibrary.ConvertPipsToDeltaPrice(extraPips, _symbol.PipSize) + _symbol.Spread : 
                MathLibrary.ConvertPipsToDeltaPrice(extraPips, _symbol.PipSize);
            var breakevenPrice = Position.TradeType == TradeType.Buy ? Position.EntryPrice + extraPrice : Position.EntryPrice - extraPrice;
            var res = Position.ModifyStopLossPrice(breakevenPrice);
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to modify position stop-loss to break-even because an error occured: {res.Error}");
                return false;
            }

            // Adds the modification of the stop-loss to the callback queue
            _modifiedStopLossQueue.Enqueue(Position);
            return true;
        }

        // Method to modify the entry take-profit of the position
        public bool ModifyEntryTakeProfit(double tpPips)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to modify position entry take-profit because it is not opened");
                return true;
            }

            var res = Position.ModifyTakeProfitPips(tpPips);
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to modify position entry take-profit because an error occured: {res.Error}");
                return false;
            }

            // Adds the modification of the take-profit to the callback queue
            _modifiedTakeProfitQueue.Enqueue(Position);
            return true;
        }

        // Method to modify the current take-profit of the position
        public bool ModifyCurrentTakeProfit(double tpPips)
        {
            if (!IsCurrentlyOpened())
            {
                _logger.Warning("Unable to modify position current take-profit because it is not opened");
                return true;
            }

            var res = Position.TradeType == TradeType.Buy ?
                Position.ModifyTakeProfitPrice(_symbol.Ask + MathLibrary.ConvertPipsToDeltaPrice(tpPips, _symbol.PipSize)) :
                Position.ModifyTakeProfitPrice(_symbol.Bid - MathLibrary.ConvertPipsToDeltaPrice(tpPips, _symbol.PipSize));
            if (!res.IsSuccessful)
            {
                _logger.Error($"Unable to modify position current take-profit because an error occured: {res.Error}");
                return false;
            }

            // Adds the modification of the take-profit to the callback queue
            _modifiedTakeProfitQueue.Enqueue(Position);
            return true;
        }

        

        // Method callback to handle open events. Only operates on its' positions
        private void PositionOpenedEventCallback(PositionOpenedEventArgs args)
        {
            var openedLabel = args.Position.Label;
            if (openedLabel == null || !openedLabel.Contains(ManagerGroupLabel))
                return;

            var openedPosition = args.Position;
            if (openedPosition.StopLoss != null)
            {
                var slPips = MathLibrary.CalculateStopLossPips(openedPosition, _symbol.PipSize);
                if (openedPosition.TakeProfit != null)
                    _logger.Info($"Opened Position: Id = {openedPosition.Id} | Direction = {openedPosition.TradeType} | Opened Lots = {openedPosition.Quantity} | SL = {slPips} Pips | Risk = {MathLibrary.CalculateRiskByVolume(slPips, openedPosition.VolumeInUnits, _robot.Account.Balance, _symbol.PipValue)}% | TP = {MathLibrary.CalculateTakeProfitPips(openedPosition, _symbol.PipSize)}");
                else
                    _logger.Info($"Opened Position: Id = {openedPosition.Id} | Direction = {openedPosition.TradeType} | Opened Lots = {openedPosition.Quantity} | SL = {slPips} Pips | Risk = {MathLibrary.CalculateRiskByVolume(slPips, openedPosition.VolumeInUnits, _robot.Account.Balance, _symbol.PipValue)}% ");
            }
            else
            {
                if (openedPosition.TakeProfit != null)
                    _logger.Info($"Opened Position: Id = {openedPosition.Id} | Direction = {openedPosition.TradeType} | Opened Lots = {openedPosition.Quantity} | TP = {MathLibrary.CalculateTakeProfitPips(openedPosition, _symbol.PipSize)} Pips");
                else
                    _logger.Info($"Opened Position: Id = {openedPosition.Id} | Direction = {openedPosition.TradeType} | Opened Lots = {openedPosition.Quantity}");
            }
        }

        // Method callback to handle modify events. Only operates on its' positions
        private void PositionModifiedEventCallback(PositionModifiedEventArgs args)
        {
            var modifiedLabel = args.Position.Label;
            if (modifiedLabel == null || !modifiedLabel.Contains(ManagerGroupLabel))
                return;

            var modifiedPosition = args.Position;
            if (_modifiedStopLossQueue.Count > 0 && _modifiedStopLossQueue.Peek() == modifiedPosition)
            {
                _modifiedStopLossQueue.Dequeue();
                var slPips = MathLibrary.CalculateStopLossPips(modifiedPosition, _symbol.PipSize);
                _logger.Info($"Modified Position Stop-Loss: Id = {modifiedPosition.Id} | Direction = {modifiedPosition.TradeType} | Lots = {modifiedPosition.Quantity} | Modified SL = {slPips} Pips | Modified Risk = {MathLibrary.CalculateRiskByVolume(slPips, modifiedPosition.VolumeInUnits, _robot.Account.Balance, _symbol.PipValue)}%");
            }
            else if (_modifiedTakeProfitQueue.Count > 0 && _modifiedTakeProfitQueue.Peek() == modifiedPosition)
            {
                _modifiedTakeProfitQueue.Dequeue();
                _logger.Info($"Modified Position Take-Profit: Id = {modifiedPosition.Id} | Direction = {modifiedPosition.TradeType} | Lots = {modifiedPosition.Quantity} | Modified TP = {MathLibrary.CalculateTakeProfitPips(modifiedPosition, _symbol.PipSize)} Pips");
            }
            else if (_modifiedVolumeQueue.Count > 0 && _modifiedVolumeQueue.Peek() == modifiedPosition)
            {
                _modifiedVolumeQueue.Dequeue();
                var totalVolume = _totalVolumeQueue.Dequeue();
                var histPos = _robot.History.FindLast(modifiedPosition.Label, modifiedPosition.SymbolName, modifiedPosition.TradeType);
                var slPips = MathLibrary.CalculateStopLossPips(modifiedPosition, _symbol.PipSize);
                _logger.Info($"Closed Position Partially: Id = {modifiedPosition.Id} | Direction = {modifiedPosition.TradeType} | Closed Lots = {histPos.Quantity} ({MathLibrary.CalculatePercentageByVolume(histPos.VolumeInUnits, totalVolume)}%) | Remaining Risk = {MathLibrary.CalculateRiskByVolume(slPips, modifiedPosition.VolumeInUnits, _robot.Account.Balance, _symbol.PipValue)}% | NPL = {histPos.NetProfit}€ | Pips = {histPos.Pips}");
            }
            else
            {
                var slPips = MathLibrary.CalculateStopLossPips(modifiedPosition, _symbol.PipSize);
                _logger.Info($"Updated Trailing Stop-Loss: Id = {modifiedPosition.Id} | Direction = {modifiedPosition.TradeType} | Lots = {modifiedPosition.Quantity} | SL = {slPips} | Risk = {MathLibrary.CalculateRiskByVolume(slPips, modifiedPosition.VolumeInUnits, _robot.Account.Balance, _symbol.PipValue)}%");
            }
        }

        // Method callback to handle close events. Only operates on its' positions
        private void PositionClosedEventCallback(PositionClosedEventArgs args)
        {
            var closedLabel = args.Position.Label;
            if (closedLabel == null || !closedLabel.Contains(ManagerGroupLabel))
                return;

            var closedPosition = args.Position;
            switch (args.Reason)
            {
                case PositionCloseReason.StopLoss:
                    _logger.Info($"Position Hit Stop-Loss: Id = {closedPosition.Id} | Direction = {closedPosition.TradeType} | Closed Lots = {closedPosition.Quantity} ({MathLibrary.CalculatePercentageByVolume(closedPosition.VolumeInUnits, _positionTotalVolume)}%) | NPL = {closedPosition.NetProfit}€ | Pips = {closedPosition.Pips}");
                    break;
                case PositionCloseReason.TakeProfit:
                    _logger.Info($"Position Hit Take-Profit: Id = {closedPosition.Id} | Direction = {closedPosition.TradeType} | Closed Lots = {closedPosition.Quantity} ({MathLibrary.CalculatePercentageByVolume(closedPosition.VolumeInUnits, _positionTotalVolume)}%) | NPL = {closedPosition.NetProfit}€ | Pips = {closedPosition.Pips}");
                    break;
                case PositionCloseReason.StopOut:
                    _logger.Info($"Position Hit Stop-Out: Id = {closedPosition.Id} | Direction = {closedPosition.TradeType} | Closed Lots = {closedPosition.Quantity} ({MathLibrary.CalculatePercentageByVolume(closedPosition.VolumeInUnits, _positionTotalVolume)}%) | NPL = {closedPosition.NetProfit}€ | Pips = {closedPosition.Pips}");
                    break;
                case PositionCloseReason.Closed:
                    if (_totalVolumeQueue.Count == 0) { break; }
                    var totalVolume = _totalVolumeQueue.Dequeue();
                    _logger.Info($"Closed Position Totally: Id = {closedPosition.Id} | Direction = {closedPosition.TradeType} | Closed Lots = {closedPosition.Quantity} ({MathLibrary.CalculatePercentageByVolume(closedPosition.VolumeInUnits, totalVolume)}%) | NPL = {closedPosition.NetProfit}€ | Pips = {closedPosition.Pips}");
                    break;
            }
        }
    }
}