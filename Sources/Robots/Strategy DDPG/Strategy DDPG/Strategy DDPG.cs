using System;
using cAlgo.API;

namespace cAlgo.Robots;

[Robot(AccessRights = AccessRights.FullAccess)]
public class StrategyDDPG : Robot
{
    private RobotAPI _strategy;

    [Parameter("Console Verbose", DefaultValue = Logging.VerboseType.Alert)]
    public Logging.VerboseType Console { get; set; }
    [Parameter("Telegram Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType Telegram { get; set; }
    [Parameter("File Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType File { get; set; }

    protected override void OnStart() { _strategy = new DDPG(this, Console, Telegram, File); }

    protected override void OnError(Error error) { _strategy.OnError(error); }

    protected override void OnException(Exception exception) { _strategy.OnException(exception); }

    protected override void OnStop() { _strategy.OnShutdown(); }
}

public class DDPG : RobotAPI { public DDPG(Robot robot, Logging.VerboseType console, Logging.VerboseType telegram, Logging.VerboseType file) : base(robot, console, telegram, file) { } }
