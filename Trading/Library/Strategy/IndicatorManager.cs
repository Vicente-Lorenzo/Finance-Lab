namespace AlgorithmicTrading.Strategy
{
    public class IndicatorManager
    {
        // Save the enumerators
        public enum TriggerMode { None, Confirmation, Signal };
        public enum TradeMode { Both, Entry, Exit };
        
        // Save a list with the respective indicators
        private readonly List<Func<bool>> _entrySignalBuyIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _entryConfirmationBuyIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _entrySignalSellIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _entryConfirmationSellIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _exitSignalBuyIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _exitConfirmationBuyIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _exitSignalSellIndicators = new List<Func<bool>>();
        private readonly List<Func<bool>> _exitConfirmationSellIndicators = new List<Func<bool>>();

        // Auxiliary function to add entry indicators according to the trigger mode
        private void AddEntryIndicator(TriggerMode triggerMode, Func<bool> buyConfirmation, Func<bool> sellConfirmation, Func<bool> buySignal, Func<bool> sellSignal)
        {
            if (triggerMode == TriggerMode.Confirmation)
            {
                _entryConfirmationBuyIndicators.Add(buyConfirmation);
                _entryConfirmationSellIndicators.Add(sellConfirmation);
            }
            else
            {
                _entryConfirmationBuyIndicators.Add(buyConfirmation);
                _entryConfirmationSellIndicators.Add(sellConfirmation);
                _entrySignalBuyIndicators.Add(buySignal);
                _entrySignalSellIndicators.Add(sellSignal);
            }
        }

        // Auxiliary function to add exit indicators according to the trigger mode
        private void AddExitIndicator(TriggerMode triggerMode, Func<bool> buyConfirmation, Func<bool> sellConfirmation, Func<bool> buySignal, Func<bool> sellSignal)
        {
            if (triggerMode == TriggerMode.Confirmation)
            {
                _exitConfirmationBuyIndicators.Add(sellConfirmation);
                _exitConfirmationSellIndicators.Add(buyConfirmation);
            }
            else
            {
                _exitConfirmationBuyIndicators.Add(sellConfirmation);
                _exitConfirmationSellIndicators.Add(buyConfirmation);
                _exitSignalBuyIndicators.Add(sellSignal);
                _exitSignalSellIndicators.Add(buySignal);
            }
        }

        // Auxiliary function to check all indicators of a given list. Returns false if the list is empty
        private static bool CheckIndicators(List<Func<bool>> confirmationList, List<Func<bool>> signalList)
        {
            if (confirmationList.Count == 0 && signalList.Count == 0)
                return false;
            
            if (signalList.Count == 0)
            {
                foreach (var confirmation in confirmationList)
                {
                    if (!confirmation())
                        return false;
                }
                return true;
            }
            else
            {
                foreach (var signal in signalList)
                {
                    if (signal())
                    {
                        foreach (var confirmation in confirmationList)
                        {
                            if (!confirmation())
                                return false;
                        }
                        return true;
                    }
                }
                return false;
            }
        }

        // Add indicator according to the trade mode and trigger mode
        public bool AddIndicator(TriggerMode triggerMode, TradeMode tradeMode, Func<bool> buyConfirmation, Func<bool> sellConfirmation, Func<bool> buySignal, Func<bool> sellSignal)
        {
            if (triggerMode == TriggerMode.None)
                return false;

            if (tradeMode == TradeMode.Entry)
            {
                AddEntryIndicator(triggerMode, buyConfirmation, sellConfirmation, buySignal, sellSignal);
                return true;
            }
            else if (tradeMode == TradeMode.Exit)
            {
                AddExitIndicator(triggerMode, buyConfirmation, sellConfirmation, buySignal, sellSignal);
                return true;
            }
            else
            {
                AddEntryIndicator(triggerMode, buyConfirmation, sellConfirmation, buySignal, sellSignal);
                AddExitIndicator(triggerMode, buyConfirmation, sellConfirmation, buySignal, sellSignal);
                return true;
            }
        }

        // Check the indicators in the entry buy list
        public bool CheckEntryBuyIndicators()
        {
            return CheckIndicators(_entryConfirmationBuyIndicators, _entrySignalBuyIndicators);
        }

        // Check the indicators in the entry sell list
        public bool CheckEntrySellIndicators()
        {
            return CheckIndicators(_entryConfirmationSellIndicators, _entrySignalSellIndicators);
        }

        // Check the indicators in the exit buy list
        public bool CheckExitBuyIndicators()
        {
            return CheckIndicators(_exitConfirmationBuyIndicators, _exitSignalBuyIndicators);
        }

        // Check the indicators in the exit sell list
        public bool CheckExitSellIndicators()
        {
            return CheckIndicators(_exitConfirmationSellIndicators, _exitSignalSellIndicators);
        }
    }
}
