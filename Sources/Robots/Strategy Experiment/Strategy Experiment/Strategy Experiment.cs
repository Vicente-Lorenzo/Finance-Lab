using System;
using cAlgo.API;

namespace cAlgo.Robots;

[Robot(AccessRights = AccessRights.FullAccess)]
public class StrategyExperiment : Robot
{
    private Strategy _strategy;

    [Parameter("Console Verbose", DefaultValue = Logging.VerboseType.Alert)]
    public Logging.VerboseType Console { get; set; }
    [Parameter("Telegram Verbose", DefaultValue = Logging.VerboseType.Silent)]
    public Logging.VerboseType Telegram { get; set; }

    protected override void OnStart() { _strategy = new Experiment(this, Console, Telegram); }

    protected override void OnError(Error error) { _strategy.OnError(error); }

    protected override void OnException(Exception exception) { _strategy.OnException(exception); }

    protected override void OnStop() { _strategy.OnShutdown(); }
}

public class Experiment : Strategy { public Experiment(Robot robot, Logging.VerboseType console, Logging.VerboseType telegram) : base(robot, console, telegram) { } }
