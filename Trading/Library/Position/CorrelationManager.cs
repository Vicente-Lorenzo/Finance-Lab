using cAlgo.API;
using AlgorithmicTrading.Log;

namespace AlgorithmicTrading.Position
{
    public class CorrelationManager
    {
        // Correlational Symbol List
        private readonly string[] _correlationalSymbolList =
        {
            "EURUSD",
            "GBPUSD",
            "EURJPY",
            "USDJPY",
            "AUDUSD",
            "USDCHF",
            "GBPJPY",
            "USDCAD",
            "EURGBP",
            "EURCHF",
            "AUDJPY",
            "NZDUSD",
            "CHFJPY",
            "EURAUD",
            "CADJPY",
            "GBPAUD",
            "EURCAD",
            "AUDCAD",
            "GBPCHF",
            "AUDCHF",
            "GBPCAD",
            "GBPNZD",
            "NZDCAD",
            "NZDCHF",
            "NZDJPY",
            "AUDNZD",
            "CADCHF",
            "EURNZD"
        };
        
        // Symbol Attributes
        private readonly bool _isCorrelationalSymbol;
        private readonly string _symbolBaseCurrency;
        private readonly string _symbolQuoteCurrency;
        
        // Correlation constant label Attributes
        private readonly string _visibleCorrelationGroupLabel;
        
        // Other Attributes
        private readonly Robot _robot;
        private readonly SpecificLogger _logger;
        
        public CorrelationManager(string correlationId, Robot robot, Logger logger)
        {
            // Initializes the Correlation group label
            _visibleCorrelationGroupLabel = null; // LabelManager.BuildCorrelationGroupLabel(correlationId, true);
            
            // Saves the other attributes
            _robot = robot;
            _logger = new SpecificLogger(logger, "CorrelationManager", correlationId);

            // Checks if it is a correlational symbol
            if (!_correlationalSymbolList.Contains(_robot.SymbolName))
            {
                _isCorrelationalSymbol = false;
                return;
            }

            // If it is a correlational symbol saves the base currency and the quote currency
            _isCorrelationalSymbol = true; 
            _symbolBaseCurrency = _robot.Symbol.Name.Substring(0, (_robot.Symbol.Name.Length / 2));
            _symbolQuoteCurrency = _robot.Symbol.Name.Substring((_robot.Symbol.Name.Length / 2), _robot.Symbol.Name.Length - _symbolBaseCurrency.Length);
        }
        
        // Method to detect correlations between other pairs. Only checks positions with correlation visible label
        internal bool DetectCorrelation(TradeType ttype)
        {
            if (!_isCorrelationalSymbol)
                return false;
            
            foreach (var pos in _robot.Positions)
            {
                if (pos.Label == null || !pos.Label.Contains(_visibleCorrelationGroupLabel))
                    continue;
                var otherBaseCurrency = pos.SymbolName.Substring(0, 3);
                var otherQuoteCurrency = pos.SymbolName.Substring(3, 3);
                if (pos.TradeType == ttype)
                {
                    if (_symbolBaseCurrency.Equals(otherBaseCurrency))
                    {
                        _logger.Warning($"Correlation base-base currency detected to opened position with Id = {pos.Id}");
                        return true;
                    }

                    if (_symbolQuoteCurrency.Equals(otherQuoteCurrency))
                    {
                        _logger.Warning($"Correlation quote-quote currency detected to opened position with Id = {pos.Id}");
                        return true;
                    }
                }
                else
                {
                    if (_symbolQuoteCurrency.Equals(otherBaseCurrency))
                    {
                        _logger.Warning($"Correlation quote-base currency detected to opened position with Id = {pos.Id}");
                        return true;
                    }

                    if (_symbolBaseCurrency.Equals(otherQuoteCurrency))
                    {
                        _logger.Warning($"Correlation base-quote currency detected to opened position with Id = {pos.Id}");
                        return true;
                    }
                }
            }
            return false;
        }
    }
}