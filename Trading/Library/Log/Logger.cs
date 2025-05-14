using cAlgo.API;

namespace AlgorithmicTrading.Log
{
    public class Logger
    {
        public enum VerboseLevel { Quiet, Error, Warn, Info, Debug }
        private readonly VerboseLevel _maxVerboseLevel;
        private readonly Robot _robot;
        private readonly Telegram? _telegram;

        internal readonly string DefaultErrorLog;
        internal readonly string DefaultWarningLog;
        internal readonly string DefaultInfoLog;
        internal readonly string DefaultDebugLog;

        public Logger(VerboseLevel maxVerboseLevel, Robot robot, Telegram? telegram = null)
        {
            _maxVerboseLevel = maxVerboseLevel;
            _robot = robot;
            _telegram = telegram;

            DefaultErrorLog = BuildDefaultLog(VerboseLevel.Error);
            DefaultWarningLog = BuildDefaultLog(VerboseLevel.Warn);
            DefaultInfoLog = BuildDefaultLog(VerboseLevel.Info);
            DefaultDebugLog = BuildDefaultLog(VerboseLevel.Debug);
        }

        private string BuildDefaultLog(VerboseLevel verboseLevel)
        {
            return $"[ {_robot.SymbolName}-{_robot.TimeFrame} ] @ [ {verboseLevel} ] ";
        }

        private void LogMessage(VerboseLevel customVerboseLevel, string defaultLog, string message)
        {
            if (customVerboseLevel > _maxVerboseLevel)
                return;
            string logMessage = defaultLog + message;
            _robot.Print(logMessage);
            _telegram?.SendText(logMessage);
        }

        internal static string BuildSpecificLog(string atClass, string? tag)
        {
            return tag != null ? $"@ [ {atClass} ] @ [ {tag} ] " : $"@ [ {atClass} ] ";
        }

        internal void LogSpecificMessage(VerboseLevel customVerboseLevel, string defaultLog, string specificLog, string message)
        {
            if (customVerboseLevel > _maxVerboseLevel)
                return;
            _robot.Print(defaultLog + specificLog + message);
            _telegram?.SendText(defaultLog + message);
        }

        public void Error(string message) { LogMessage(VerboseLevel.Error, DefaultErrorLog, message); }
        public void Warning(string message) { LogMessage(VerboseLevel.Warn, DefaultWarningLog, message); }
        public void Info(string message) { LogMessage(VerboseLevel.Info, DefaultInfoLog, message); }
        public void Debug(string message) { LogMessage(VerboseLevel.Debug, DefaultDebugLog, message); }
    }
}