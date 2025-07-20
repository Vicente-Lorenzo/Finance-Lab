using System;
using cAlgo.API;

namespace cAlgo.Robots;

[Robot(AccessRights = AccessRights.FullAccess)]
public class StrategyDownload : Robot
{
    private RobotAPI _robotApi;
    
    [Parameter("Console Verbose", DefaultValue = Logging.VerboseType.Debug)]
    public Logging.VerboseType Console { get; set; }
    [Parameter("Telegram Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType Telegram { get; set; }
    [Parameter("File Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType File { get; set; }

    protected override void OnStart() { _robotApi = new Download(this, Console, Telegram, File); }

    protected override void OnError(Error error) { _robotApi.OnError(error); }

    protected override void OnException(Exception exception) { _robotApi.OnException(exception); }

    protected override void OnStop() { _robotApi.OnShutdown(); }
}

public class Download : RobotAPI { public Download(Robot robot, Logging.VerboseType console, Logging.VerboseType telegram, Logging.VerboseType file) : base(robot, console, telegram, file) { } }
