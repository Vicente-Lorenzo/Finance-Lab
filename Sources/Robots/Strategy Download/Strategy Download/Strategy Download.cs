using System;
using cAlgo.API;

namespace cAlgo.Robots;

[Robot(AccessRights = AccessRights.FullAccess)]
public class StrategyDownload : Robot
{
    private RobotAPI _robotApi;
    
    [Parameter("Console Verbose", DefaultValue = Logging.VerboseType.Alert)]
    public Logging.VerboseType Console { get; set; }
    [Parameter("Telegram Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType Telegram { get; set; }

    protected override void OnStart() { _robotApi = new Download(this, Console, Telegram); }

    protected override void OnError(Error error) { _robotApi.OnError(error); }

    protected override void OnException(Exception exception) { _robotApi.OnException(exception); }

    protected override void OnStop() { _robotApi.OnShutdown(); }
}

public class Download : RobotAPI { public Download(Robot robot, Logging.VerboseType console, Logging.VerboseType telegram) : base(robot, console, telegram) { } }
