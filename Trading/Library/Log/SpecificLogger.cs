namespace AlgorithmicTrading.Log
{
    public class SpecificLogger
    {
        private readonly Logger _logger;
        private readonly string _defaultSpecificLog;

        public SpecificLogger(Logger logger, string atClass, string? tag = null)
        {
            _logger = logger;
            _defaultSpecificLog = Logger.BuildSpecificLog(atClass, tag);
        }

        public void Error(string message) { _logger.LogSpecificMessage(Logger.VerboseLevel.Error, _logger.DefaultErrorLog, _defaultSpecificLog, message); }
        public void Warning(string message) { _logger.LogSpecificMessage(Logger.VerboseLevel.Warn, _logger.DefaultWarningLog, _defaultSpecificLog, message); }
        public void Info(string message) { _logger.LogSpecificMessage(Logger.VerboseLevel.Info, _logger.DefaultInfoLog, _defaultSpecificLog, message); }
        public void Debug(string message) { _logger.LogSpecificMessage(Logger.VerboseLevel.Debug, _logger.DefaultDebugLog, _defaultSpecificLog, message); }
    }
}
