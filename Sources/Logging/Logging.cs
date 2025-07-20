using cAlgo.API.Internals;

namespace cAlgo.Robots;

public class Logging
{
    public enum VerboseType
    {
        Silent = 0,
        Critical = 1,
        Error = 2,
        Warning = 3,
        Alert = 4,
        Info = 5,
        Debug = 6
    }
    
    private readonly Algo _algo;
    private readonly VerboseType _verbose;
    private readonly string _cname;
    private const string DefaultCriticalLog = "CRITICAL";
    private const string DefaultErrorLog = "ERROR";
    private const string DefaultWarningLog = "WARNING";
    private const string DefaultInfoLog = "INFO";
    private const string DefaultDebugLog = "DEBUG";
    private const string DefaultAlertLog = "ALERT";
    
    public Logging(Algo algo, string cname, VerboseType verbose)
    {
        _algo = algo;
        _cname = cname;
        _verbose = verbose;
    }

    private void LogMessage(VerboseType verbose, string defaultLog, string message)
    { 
        if (_verbose < verbose) return;
        var logMessage = $"{defaultLog} - {_cname} - {message}";
        _algo.Print(logMessage);
    }

    public void Critical(string message) => LogMessage(VerboseType.Critical, DefaultCriticalLog, message);
    public void Error(string message) => LogMessage(VerboseType.Error, DefaultErrorLog, message);
    public void Warning(string message) => LogMessage(VerboseType.Warning, DefaultWarningLog, message); 
    public void Info(string message) => LogMessage(VerboseType.Info, DefaultInfoLog, message); 
    public void Debug(string message) => LogMessage(VerboseType.Debug, DefaultDebugLog, message);
    public void Alert(string message) => LogMessage(VerboseType.Alert, DefaultAlertLog, message);
}
