using System;
using System.IO;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;

namespace cAlgo.Robots;

public abstract class RobotAPI
{
    public enum UpdateID
    {
        Complete = 0,
        Runtime = 1,
        Account = 2,
        Symbol = 3,
        OpenedBuy = 4,
        OpenedSell = 5,
        ModifiedBuyVolume = 6,
        ModifiedSellVolume = 7,
        ModifiedBuyStopLoss = 8,
        ModifiedSellStopLoss = 9,
        ModifiedBuyTakeProfit = 10,
        ModifiedSellTakeProfit = 11,
        ClosedBuy = 12,
        ClosedSell = 13,
        BarClosed = 14,
        TickClosed = 15,
        AskAboveTarget = 16,
        AskBelowTarget = 17,
        BidAboveTarget = 18,
        BidBelowTarget = 19,
        Shutdown = 20
    }

    public enum ActionID
    {
        Complete = 0,
        OpenBuy = 1,
        OpenSell = 2,
        ModifyBuyVolume = 3,
        ModifySellVolume = 4,
        ModifyBuyStopLoss = 5,
        ModifySellStopLoss = 6,
        ModifyBuyTakeProfit = 7,
        ModifySellTakeProfit = 8,
        CloseBuy = 9,
        CloseSell = 10,
        AskAboveTarget = 11,
        AskBelowTarget = 12,
        BidAboveTarget = 13,
        BidBelowTarget = 14
    }

    public enum PositionType
    {
        Normal = 0,
        Continuation = 1
    }

    public enum TickMode
    {
        Accurate = 0,
        Inaccurate = 1
    }

    public class xTick
    {
        public DateTime Timestamp { get; set; }
        public double Ask { get; set; }
        public double Bid { get; set; }
        public double AskBaseConversionRate { get; set; }
        public double BidBaseConversionRate { get; set; }
        public double AskQuoteConversionRate { get; set; }
        public double BidQuoteConversionRate { get; set; }
    }

    public class xBar
    {
        public DateTime Timestamp { get; set; }
        public xTick GapTick { get; set; }
        public xTick OpenTick { get; set; }
        public xTick HighTick { get; set; }
        public xTick LowTick { get; set; }
        public xTick CloseTick { get; set; }
        public double TickVolume { get; set; }
    }

    private class LastPositionData
    {
        public double LastVolume { get; set; }
        public double? LastStopLoss { get; set; }
        public double? LastTakeProfit { get; set; }
    }

    private readonly Robot robot;
    private readonly Logging log;
    private readonly SystemAPI system;

    private readonly Func<double> askBaseConversionRate;
    private readonly Func<double> bidBaseConversionRate;
    private readonly Func<double> askQuoteConversionRate;
    private readonly Func<double> bidQuoteConversionRate;

    private readonly xBar bar;

    private readonly Dictionary<int, LastPositionData> positions;

    private double? askAboveTarget;
    private double? askBelowTarget;
    private double? bidAboveTarget;
    private double? bidBelowTarget;

    protected RobotAPI(Robot algo, Logging.VerboseType console, Logging.VerboseType telegram, Logging.VerboseType file)
    {
        robot = algo;
        log = new Logging(robot, "Strategy", console);

        (askBaseConversionRate, bidBaseConversionRate) = FindConversionRates(robot.Symbol.BaseAsset, robot.Account.Asset);
        (askQuoteConversionRate, bidQuoteConversionRate) = FindConversionRates(robot.Symbol.QuoteAsset, robot.Account.Asset);

        var tick = Tick();
        bar = new xBar
        {
            Timestamp = tick.Timestamp,
            GapTick = tick,
            OpenTick = tick,
            HighTick = tick,
            LowTick = tick,
            CloseTick = tick,
            TickVolume = 0.0
        };
        positions = new Dictionary<int, LastPositionData>();

        robot.Positions.Opened += OnPositionOpened;
        robot.Positions.Modified += OnPositionModified;
        robot.Positions.Closed += OnPositionClosed;
        robot.Bars.BarClosed += OnBarClosed;
        robot.Bars.BarOpened += OnBarOpened;
        robot.Symbol.Tick += OnTick;

        var broker = ParseBrokerName();
        var group = ParseGroupName();
        var symbol = ParseSymbolName();
        var timeframe = ParseTimeframeName();

        system = new SystemAPI(robot, broker, symbol, timeframe, console);
        system.Initialize();

        var baseDirectory = new DirectoryInfo(Environment.CurrentDirectory).Parent?.Parent?.Parent?.FullName;
        var scriptName = GetType().Name;
        var scriptArgs = $"\"Realtime\" --console \"{console}\" --telegram \"{telegram}\" --file \"{file}\" --strategy \"{scriptName}\" --broker \"{broker}\" --group \"{group}\" --symbol \"{symbol}\" --timeframe \"{timeframe}\" --iid \"{this.robot.InstanceId}\"";
        var psi = new ProcessStartInfo
        {
            FileName = "cmd.exe",
            Arguments = $"/k \"cd {baseDirectory} && conda activate trading && python -m Library.Robots.Main {scriptArgs}\"",
            WindowStyle = ProcessWindowStyle.Minimized,
            UseShellExecute = true
        };
        Process.Start(psi);

        system.Connect();

        system.SendUpdateRuntime(robot.RunningMode, DetectTickMode());
        system.SendUpdateAccount(robot.Account);
        system.SendUpdateSymbol(robot.Symbol);
        system.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private TickMode DetectTickMode()
    {
        try { return robot.MarketData.GetTicks().Any() ? TickMode.Accurate : TickMode.Inaccurate; }
        catch { return TickMode.Inaccurate; }
    }

    private xTick Tick()
    {
        return new xTick
        {
            Timestamp = robot.Server.Time,
            Ask = robot.Symbol.Ask,
            Bid = robot.Symbol.Bid,
            AskBaseConversionRate = askBaseConversionRate(),
            BidBaseConversionRate = bidBaseConversionRate(),
            AskQuoteConversionRate = askQuoteConversionRate(),
            BidQuoteConversionRate = bidQuoteConversionRate()
        };
    }

    private string ParseBrokerName()
    {
        return robot.Account.BrokerName.Replace(" ", "");
    }

    private string ParseGroupName()
    {
        for (var index = 1; index <= robot.Watchlists.Count() - 1; index++)
        {
            var watchlist = robot.Watchlists[index];
            if (watchlist.SymbolNames.Contains(robot.Symbol.Name))
                return watchlist.Name;
        }
        return null;
    }

    private string ParseSymbolName()
    {
        return robot.Symbol.Name.Replace(" ", "");
    }

    private string ParseTimeframeName()
    {
        return robot.TimeFrame.Name.Replace(" ", "");
    }

    private (Func<double> Ask, Func<double> Bid) FindConversionRates(Asset fromAsset, Asset toAsset)
    {
        if (fromAsset == toAsset)
            return (Ask: () => 1.0, Bid: () => 1.0);
        foreach (var symbolName in robot.Symbols)
        {
            try
            {
                if (!robot.Symbols.Exists(symbolName)) continue;
                var symbol = robot.Symbols.GetSymbol(symbolName);
                if (symbol.BaseAsset == null || symbol.QuoteAsset == null)
                    continue;
                if (symbol.BaseAsset == fromAsset && symbol.QuoteAsset == toAsset)
                    return (Ask: () => symbol.Ask, Bid: () => symbol.Bid);
                if (symbol.QuoteAsset == fromAsset && symbol.BaseAsset == toAsset)
                    return (Ask: () => 1.0 / symbol.Bid, Bid: () => 1.0 / symbol.Ask);
            }
            catch (Exception e) { log.Warning(e.Message); }
        }
        throw new Exception($"No conversion symbol found for {fromAsset} → {toAsset}");
    }

    private bool IsPositionFromRobot(Position position)
    {
        return string.Equals(position.Label, robot.InstanceId);
    }

    private Position[] FindPositions()
    {
        return robot.Positions.FindAll(robot.InstanceId);
    }

    private Position FindPosition(int positionId)
    {
        return FindPositions().FirstOrDefault(p => p.Id == positionId);
    }

    private HistoricalTrade[] FindTrades()
    {
        return robot.History.FindAll(robot.InstanceId);
    }

    private HistoricalTrade FindTrade(int positionId)
    {
        return FindTrades().FirstOrDefault(t => t.PositionId == positionId);
    }

    private void OnPositionOpened(PositionOpenedEventArgs args)
    {
        if (!IsPositionFromRobot(args.Position))
            return;
        var positionData = new LastPositionData
        {
            LastVolume = args.Position.VolumeInUnits,
            LastStopLoss = args.Position.StopLoss,
            LastTakeProfit = args.Position.TakeProfit
        };
        if (args.Position.TradeType == TradeType.Buy)
            system.SendUpdateOpenedBuy(bar, robot.Account, args.Position);
        else
            system.SendUpdateOpenedSell(bar, robot.Account, args.Position);
        positions.Add(args.Position.Id, positionData);
        system.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private void OnPositionModified(PositionModifiedEventArgs args)
    {
        if (!IsPositionFromRobot(args.Position))
            return;
        var positionData = positions[args.Position.Id];
        if (Math.Abs(args.Position.VolumeInUnits - positionData.LastVolume) > double.Epsilon)
        {
            var trade = FindTrade(args.Position.Id);
            if (args.Position.TradeType == TradeType.Buy)
                system.SendUpdateModifiedBuyVolume(bar, robot.Account, args.Position, trade);
            else
                system.SendUpdateModifiedSellVolume(bar, robot.Account, args.Position, trade);
            positionData.LastVolume = args.Position.VolumeInUnits;
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            return;
        }
        if ((positionData.LastStopLoss == null && args.Position.StopLoss != null) ||
            (positionData.LastStopLoss != null && args.Position.StopLoss == null) ||
            (positionData.LastStopLoss != null && args.Position.StopLoss != null && Math.Abs((double)args.Position.StopLoss - (double)positionData.LastStopLoss) > double.Epsilon))
        {
            if (args.Position.TradeType == TradeType.Buy)
                system.SendUpdateModifiedBuyStopLoss(bar, robot.Account, args.Position);
            else
                system.SendUpdateModifiedSellStopLoss(bar, robot.Account, args.Position);
            positionData.LastStopLoss = args.Position.StopLoss;
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            return;
        }
        if ((positionData.LastTakeProfit == null && args.Position.TakeProfit != null) ||
            (positionData.LastTakeProfit != null && args.Position.TakeProfit == null) ||
            (positionData.LastTakeProfit != null && args.Position.TakeProfit != null && Math.Abs((double)args.Position.TakeProfit - (double)positionData.LastTakeProfit) > double.Epsilon))
        {
            if (args.Position.TradeType == TradeType.Buy)
                system.SendUpdateModifiedBuyTakeProfit(bar, robot.Account, args.Position);
            else
                system.SendUpdateModifiedSellTakeProfit(bar, robot.Account, args.Position);
            positionData.LastTakeProfit = args.Position.TakeProfit;
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
    }

    private void OnPositionClosed(PositionClosedEventArgs args)
    {
        if (!IsPositionFromRobot(args.Position))
            return;
        var trade = FindTrade(args.Position.Id);
        if (args.Position.TradeType == TradeType.Buy)
            system.SendUpdateClosedBuy(bar, robot.Account, trade);
        else
            system.SendUpdateClosedSell(bar, robot.Account, trade);
        positions.Remove(args.Position.Id);
        system.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private void OnBarClosed(BarClosedEventArgs args)
    {
        var lastBar = robot.Bars.LastBar;
        bar.TickVolume = lastBar.TickVolume;
        system.SendUpdateBarClosed(bar);
        system.SendUpdateComplete();
        ReceiveAndProcessActions();
        bar.Timestamp = lastBar.OpenTime;
        bar.GapTick = bar.CloseTick;
    }

    private void OnBarOpened(BarOpenedEventArgs args)
    {
        var tick = Tick();
        bar.OpenTick = tick;
        bar.HighTick = tick;
        bar.LowTick = tick;
        bar.CloseTick = tick;
    }

    private void OnTick(SymbolTickEventArgs args)
    {
        var tick = Tick();

        if (tick.Ask > bar.HighTick.Ask)
        {
            bar.HighTick.Timestamp = tick.Timestamp;
            bar.HighTick.Ask = tick.Ask;
            bar.HighTick.AskBaseConversionRate = tick.AskBaseConversionRate;
            bar.HighTick.BidBaseConversionRate = tick.BidBaseConversionRate;
            bar.HighTick.AskQuoteConversionRate = tick.AskQuoteConversionRate;
            bar.HighTick.BidQuoteConversionRate = tick.BidQuoteConversionRate;
        }
        if (tick.Ask < bar.LowTick.Ask)
        {
            bar.LowTick.Timestamp = tick.Timestamp;
            bar.LowTick.Ask = tick.Ask;
            bar.LowTick.AskBaseConversionRate = tick.AskBaseConversionRate;
            bar.LowTick.BidBaseConversionRate = tick.BidBaseConversionRate;
            bar.LowTick.AskQuoteConversionRate = tick.AskQuoteConversionRate;
            bar.LowTick.BidQuoteConversionRate = tick.BidQuoteConversionRate;
        }
        if (tick.Bid > bar.HighTick.Bid)
        {
            bar.HighTick.Timestamp = tick.Timestamp;
            bar.HighTick.Bid = tick.Bid;
            bar.HighTick.AskBaseConversionRate = tick.AskBaseConversionRate;
            bar.HighTick.BidBaseConversionRate = tick.BidBaseConversionRate;
            bar.HighTick.AskQuoteConversionRate = tick.AskQuoteConversionRate;
            bar.HighTick.BidQuoteConversionRate = tick.BidQuoteConversionRate;
        }
        if (tick.Bid < bar.LowTick.Bid)
        {
            bar.LowTick.Timestamp = tick.Timestamp;
            bar.LowTick.Bid = tick.Bid;
            bar.LowTick.AskBaseConversionRate = tick.AskBaseConversionRate;
            bar.LowTick.BidBaseConversionRate = tick.BidBaseConversionRate;
            bar.LowTick.AskQuoteConversionRate = tick.AskQuoteConversionRate;
            bar.LowTick.BidQuoteConversionRate = tick.BidQuoteConversionRate;
        }
        bar.CloseTick = tick;

        var update = false;
        if (askAboveTarget != null && tick.Ask >= askAboveTarget)
        {
            system.SendUpdateAskAboveTarget(tick);
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            update = true;
        }
        if (askBelowTarget != null && tick.Ask <= askBelowTarget)
        {
            system.SendUpdateAskBelowTarget(tick);
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            update = true;
        }
        if (bidAboveTarget != null && tick.Bid >= bidAboveTarget)
        {
            system.SendUpdateBidAboveTarget(tick);
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            update = true;
        }
        if (bidBelowTarget != null && tick.Bid <= bidBelowTarget)
        {
            system.SendUpdateBidBelowTarget(tick);
            system.SendUpdateComplete();
            ReceiveAndProcessActions();
            update = true;
        }

        if (update) return;
        system.SendUpdateTickClosed(tick);
        system.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    public void OnError(Error error)
    {
        log.Error("An unexpected error occurred in the robot execution");
        log.Error(error.TradeResult.ToString());
    }

    public void OnException(Exception exception)
    {
        log.Error("An unexpected exception occurred in the robot execution");
        log.Error(exception.ToString());
    }

    public void OnShutdown()
    {
        log.Warning("Shutdown strategy and safely terminate operations");
        system.SendUpdateShutdown();
        ReceiveAndProcessActions();
        system.Disconnect();
    }

    private bool ProcessActionOpenPosition(TradeType tradeType, PositionType posType, double volume, double? slPips, double? tpPips)
    {
        var result = robot.ExecuteMarketOrder(tradeType, robot.Symbol.Name, volume, robot.InstanceId, slPips, tpPips, posType.ToString(), false, StopTriggerMethod.Trade);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyVolume(int positionID, double volume)
    {
        var position = FindPosition(positionID);
        if (position == null) { log.Warning("Modify Volume did not find the position"); return true; }
        if (Math.Abs(position.VolumeInUnits - volume) < robot.Symbol.VolumeInUnitsMin)
            log.Warning("Modified Volume to the same value causing unexpected behaviour");
        var result = position.ModifyVolume(volume);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyStopLoss(int positionID, double? slPrice)
    {
        var position = FindPosition(positionID);
        if (position == null) { log.Warning("Modify Stop Loss did not find the position"); return true;}
        if (position.StopLoss != null && slPrice != null && Math.Abs((double)position.StopLoss - (double)slPrice) < robot.Symbol.TickSize)
            log.Warning("Modified Stop-Loss to the same value causing unexpected behaviour");
        var result = position.ModifyStopLossPrice(slPrice);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyTakeProfit(int positionID, double? tpPrice)
    {
        var position = FindPosition(positionID);
        if (position == null) { log.Warning("Modify Take Profit did not find the position"); return true; }
        if (position.TakeProfit != null && tpPrice != null && Math.Abs((double)position.TakeProfit - (double)tpPrice) < robot.Symbol.TickSize)
            log.Warning("Modified Take-Profit to the same value causing unexpected behaviour");
        var result = position.ModifyTakeProfitPrice(tpPrice);
        return result.IsSuccessful;
    }

    private bool ProcessActionClosePosition(int positionID)
    {
        var position = FindPosition(positionID);
        if (position == null) { log.Warning("Close Position did not find the position"); return true; }
        return robot.ClosePosition(position).IsSuccessful;
    }

    private void ReceiveAndProcessActions()
    {
        ActionID actionID;
        do
        {
            actionID = system.ReceiveActionID();
            int positionID;
            PositionType posType;
            double volume;
            double? slPrice, tpPrice;
            switch (actionID)
            {
                case ActionID.Complete:
                    break;
                case ActionID.OpenBuy:
                    (posType, volume, slPrice, tpPrice) = system.ReceiveActionOpen();
                    if (!ProcessActionOpenPosition(TradeType.Buy, posType, volume, slPrice, tpPrice)) robot.Stop();
                    break;
                case ActionID.OpenSell:
                    (posType, volume, slPrice, tpPrice) = system.ReceiveActionOpen();
                    if (!ProcessActionOpenPosition(TradeType.Sell, posType, volume, slPrice, tpPrice)) robot.Stop();
                    break;
                case ActionID.ModifyBuyVolume:
                case ActionID.ModifySellVolume:
                    (positionID, volume) = system.ReceiveActionModifyVolume();
                    if (!ProcessActionModifyVolume(positionID, volume)) robot.Stop();
                    break;
                case ActionID.ModifyBuyStopLoss:
                case ActionID.ModifySellStopLoss:
                    (positionID, slPrice) = system.ReceiveActionModifyStopLoss();
                    if (!ProcessActionModifyStopLoss(positionID, slPrice)) robot.Stop();
                    break;
                case ActionID.ModifyBuyTakeProfit:
                case ActionID.ModifySellTakeProfit:
                    (positionID, tpPrice) = system.ReceiveActionModifyTakeProfit();
                    if (!ProcessActionModifyTakeProfit(positionID, tpPrice)) robot.Stop();
                    break;
                case ActionID.CloseBuy:
                case ActionID.CloseSell:
                    positionID = system.ReceiveActionClose();
                    if (!ProcessActionClosePosition(positionID)) robot.Stop();
                    break;
                case ActionID.AskAboveTarget:
                    askAboveTarget = system.ReceiveActionAskAboveTarget();
                    break;
                case ActionID.AskBelowTarget:
                    askBelowTarget = system.ReceiveActionAskBelowTarget();
                    break;
                case ActionID.BidAboveTarget:
                    bidAboveTarget = system.ReceiveActionBidAboveTarget();
                    break;
                case ActionID.BidBelowTarget:
                    bidBelowTarget = system.ReceiveActionBidBelowTarget();
                    break;
                default:
                    log.Critical($"Received invalid action ID: {actionID}");
                    throw new ArgumentOutOfRangeException();
            }
        } while (actionID != ActionID.Complete);
    }
}