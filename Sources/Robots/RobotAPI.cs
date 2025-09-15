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
        Account = 1,
        Symbol = 2,
        OpenedBuy = 3,
        OpenedSell = 4,
        ModifiedBuyVolume = 5,
        ModifiedBuyStopLoss = 6,
        ModifiedBuyTakeProfit = 7,
        ModifiedSellVolume = 8,
        ModifiedSellStopLoss = 9,
        ModifiedSellTakeProfit = 10,
        ClosedBuy = 11,
        ClosedSell = 12,
        BarClosed = 13,
        AskAboveTarget = 14,
        AskBelowTarget = 15,
        BidAboveTarget = 16,
        BidBelowTarget = 17,
        Shutdown = 18
    }

    public enum ActionID
    {
        Complete = 0,
        OpenBuy = 1,
        OpenSell = 2,
        ModifyBuyVolume = 3,
        ModifyBuyStopLoss = 4,
        ModifyBuyTakeProfit = 5,
        ModifySellVolume = 6,
        ModifySellStopLoss = 7,
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

    private readonly SystemAPI _systemApi;
    private readonly Robot _robot;
    private readonly Logging _logging;

    private class LastPositionData
    {
        public double LastVolume { get; set; }
        public double? LastStopLoss { get; set; }
        public double? LastTakeProfit { get; set; }
    }
    private readonly Dictionary<int, LastPositionData> _positions;

    private double? _lastAskAboveTarget;
    private double? _lastAskBelowTarget;
    private double? _lastBidAboveTarget;
    private double? _lastBidBelowTarget;

    protected RobotAPI(Robot robot, Logging.VerboseType console, Logging.VerboseType telegram, Logging.VerboseType file)
    {
        _robot = robot;
        _logging = new Logging(robot, "Strategy", console);
        _positions = new Dictionary<int, LastPositionData>();
        
        _robot.Positions.Opened += OnPositionOpened;
        _robot.Positions.Modified += OnPositionModified;
        _robot.Positions.Closed += OnPositionClosed;
        _robot.Bars.BarClosed += OnBarClosed;
        _robot.Symbol.Tick += OnTick;

        var broker = ParseBrokerName();
        var group = ParseGroupName();
        var symbol = ParseSymbolName();
        var timeframe = ParseTimeframeName();

        _systemApi = new SystemAPI(robot, broker, symbol, timeframe, console);
        _systemApi.Initialize();

        var baseDirectory = new DirectoryInfo(Environment.CurrentDirectory).Parent?.Parent?.Parent?.FullName;
        var scriptName = GetType().Name;
        var scriptArgs = $"\"Realtime\" --console \"{console}\" --telegram \"{telegram}\" --file \"{file}\" --strategy \"{scriptName}\" --broker \"{broker}\" --group \"{group}\" --symbol \"{symbol}\" --timeframe \"{timeframe}\" --iid \"{_robot.InstanceId}\"";
        var psi = new ProcessStartInfo
        {
            FileName = "cmd.exe",
            Arguments = $"/k \"cd {baseDirectory} && conda activate trading && python -m Library.Robots.Main {scriptArgs}\"",
            WindowStyle = ProcessWindowStyle.Minimized,
            UseShellExecute = true
        };
        Process.Start(psi);

        _systemApi.Connect();
        
        _systemApi.SendUpdateAccount(_robot.Account);
        _systemApi.SendUpdateSymbol(_robot.Symbol);
        for (var i = 1; i < _robot.Bars.Count - 1; i++) { _systemApi.SendUpdateBarClosed(_robot.Bars[i-1], _robot.Bars[i]); }
        _systemApi.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private string ParseBrokerName()
    {
        return _robot.Account.BrokerName.Replace(" ", "");
    }

    private string ParseGroupName()
    {
        for (var index = 1; index <= _robot.Watchlists.Count() - 1; index++)
        {
            var watchlist = _robot.Watchlists[index];
            if (watchlist.SymbolNames.Contains(_robot.Symbol.Name))
                return watchlist.Name;
        }
        return null;
    }

    private string ParseSymbolName()
    {
        return _robot.Symbol.Name.Replace(" ", "");
    }

    private string ParseTimeframeName()
    {
        return _robot.TimeFrame.Name.Replace(" ", "");
    }

    private bool IsPositionFromRobot(Position position)
    {
        return string.Equals(position.Label, _robot.InstanceId);
    }

    private Position FindPosition(int positionID)
    {
        var positions = _robot.Positions.FindAll(_robot.InstanceId);
        return !positions.Any() ? null : positions.Where(position => position.Id == positionID).OrderByDescending(position => position.EntryTime).First();
    }

    private HistoricalTrade FindTrade(int positionID)
    {
        var trades = _robot.History.FindAll(_robot.InstanceId);
        return !trades.Any() ? null : trades.Where(trade => trade.PositionId == positionID).OrderByDescending(trade => trade.ClosingTime).First();
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
            _systemApi.SendUpdateOpenedBuy(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
        else
            _systemApi.SendUpdateOpenedSell(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
        _positions.Add(args.Position.Id, positionData);
        _systemApi.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private void OnPositionModified(PositionModifiedEventArgs args)
    {
        if (!IsPositionFromRobot(args.Position))
            return;
        var positionData = _positions[args.Position.Id];
        if (Math.Abs(args.Position.VolumeInUnits - positionData.LastVolume) > double.Epsilon)
        {
            var trade = FindTrade(args.Position.Id);
            if (args.Position.TradeType == TradeType.Buy)
                _systemApi.SendUpdateModifiedBuyVolume(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position, trade);
            else
                _systemApi.SendUpdateModifiedSellVolume(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position, trade);
            positionData.LastVolume = args.Position.VolumeInUnits;
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
            return;
        }
        if ((positionData.LastStopLoss == null && args.Position.StopLoss != null) ||
            (positionData.LastStopLoss != null && args.Position.StopLoss == null) ||
            (positionData.LastStopLoss != null && args.Position.StopLoss != null && Math.Abs((double)args.Position.StopLoss - (double)positionData.LastStopLoss) > double.Epsilon))
        {
            if (args.Position.TradeType == TradeType.Buy)
                _systemApi.SendUpdateModifiedBuyStopLoss(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
            else
                _systemApi.SendUpdateModifiedSellStopLoss(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
            positionData.LastStopLoss = args.Position.StopLoss;
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
            return;
        }
        if ((positionData.LastTakeProfit == null && args.Position.TakeProfit != null) ||
            (positionData.LastTakeProfit != null && args.Position.TakeProfit == null) ||
            (positionData.LastTakeProfit != null && args.Position.TakeProfit != null && Math.Abs((double)args.Position.TakeProfit - (double)positionData.LastTakeProfit) > double.Epsilon))
        {
            if (args.Position.TradeType == TradeType.Buy)
                _systemApi.SendUpdateModifiedBuyTakeProfit(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
            else
                _systemApi.SendUpdateModifiedSellTakeProfit(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, args.Position);
            positionData.LastTakeProfit = args.Position.TakeProfit;
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
    }

    private void OnPositionClosed(PositionClosedEventArgs args)
    {
        if (!IsPositionFromRobot(args.Position))
            return;
        var trade = FindTrade(args.Position.Id);
        if (args.Position.TradeType == TradeType.Buy)
            _systemApi.SendUpdateClosedBuy(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, trade);
        else
            _systemApi.SendUpdateClosedSell(_robot.Bars.Last(1), _robot.Bars.Last(0), _robot.Account, _robot.Symbol, trade);
        _positions.Remove(args.Position.Id);
        _systemApi.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private void OnBarClosed(BarClosedEventArgs args)
    { 
        _systemApi.SendUpdateBarClosed(_robot.Bars.Last(1), _robot.Bars.Last(0));
        _systemApi.SendUpdateComplete();
        ReceiveAndProcessActions();
    }

    private void OnTick(SymbolTickEventArgs args)
    {
        if (_lastAskAboveTarget != null && args.Ask >= _lastAskAboveTarget)
        {
            _systemApi.SendUpdateAskAboveTarget(_robot.Server.Time, args.Ask, args.Bid);
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
        if (_lastAskBelowTarget != null && args.Ask <= _lastAskBelowTarget)
        {
            _systemApi.SendUpdateAskBelowTarget(_robot.Server.Time, args.Ask, args.Bid);
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
        if (_lastBidAboveTarget != null && args.Bid >= _lastBidAboveTarget)
        {
            _systemApi.SendUpdateBidAboveTarget(_robot.Server.Time, args.Ask, args.Bid);
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
        if (_lastBidBelowTarget != null && args.Bid <= _lastBidBelowTarget)
        {
            _systemApi.SendUpdateBidBelowTarget(_robot.Server.Time, args.Ask, args.Bid);
            _systemApi.SendUpdateComplete();
            ReceiveAndProcessActions();
        }
    }

    public void OnError(Error error)
    {
        _logging.Error("An unexpected error occurred in the robot execution");
        _logging.Error(error.TradeResult.ToString());
    }

    public void OnException(Exception exception)
    {
        _logging.Error("An unexpected exception occurred in the robot execution");
        _logging.Error(exception.ToString());
    }

    public void OnShutdown()
    {
        _logging.Warning("Shutdown strategy and safely terminate operations");
        _systemApi.SendUpdateShutdown();
        ReceiveAndProcessActions();
        _systemApi.Disconnect();
    }

    private bool ProcessActionOpenPosition(TradeType tradeType, PositionType posType, double volume, double? slPips, double? tpPips)
    {
        var result = _robot.ExecuteMarketOrder(tradeType, _robot.SymbolName, volume, _robot.InstanceId, slPips, tpPips, posType.ToString(), false, StopTriggerMethod.Trade);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyVolume(int positionID, double volume)
    {
        var position = FindPosition(positionID);
        if (position == null) { _logging.Warning("Modify Volume did not find the position"); return true; }
        if (Math.Abs(position.VolumeInUnits - volume) < _robot.Symbol.VolumeInUnitsMin)
            _logging.Warning("Modified Volume to the same value causing unexpected behaviour");
        var result = position.ModifyVolume(volume);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyStopLoss(int positionID, double? slPrice)
    {
        var position = FindPosition(positionID);
        if (position == null) { _logging.Warning("Modify Stop Loss did not find the position"); return true;}
        if (position.StopLoss != null && slPrice != null && Math.Abs((double)position.StopLoss - (double)slPrice) < _robot.Symbol.TickSize)
            _logging.Warning("Modified Stop-Loss to the same value causing unexpected behaviour");
        var result = position.ModifyStopLossPrice(slPrice);
        return result.IsSuccessful;
    }

    private bool ProcessActionModifyTakeProfit(int positionID, double? tpPrice)
    {
        var position = FindPosition(positionID);
        if (position == null) { _logging.Warning("Modify Take Profit did not find the position"); return true; }
        if (position.TakeProfit != null && tpPrice != null && Math.Abs((double)position.TakeProfit - (double)tpPrice) < _robot.Symbol.TickSize)
            _logging.Warning("Modified Take-Profit to the same value causing unexpected behaviour");
        var result = position.ModifyTakeProfitPrice(tpPrice);
        return result.IsSuccessful;
    }

    private bool ProcessActionClosePosition(int positionID)
    {
        var position = FindPosition(positionID);
        if (position == null) { _logging.Warning("Close Position did not find the position"); return true; }
        return _robot.ClosePosition(position).IsSuccessful;
    }

    private void ReceiveAndProcessActions()
    {
        ActionID actionID;
        do
        {
            actionID = _systemApi.ReceiveActionID();
            int positionID;
            PositionType posType;
            double volume;
            double? slPrice, tpPrice;
            switch (actionID)
            {
                case ActionID.Complete:
                    break;
                case ActionID.OpenBuy:
                    (posType, volume, slPrice, tpPrice) = _systemApi.ReceiveActionOpen();
                    if (!ProcessActionOpenPosition(TradeType.Buy, posType, volume, slPrice, tpPrice)) _robot.Stop();
                    break;
                case ActionID.OpenSell:
                    (posType, volume, slPrice, tpPrice) = _systemApi.ReceiveActionOpen();
                    if (!ProcessActionOpenPosition(TradeType.Sell, posType, volume, slPrice, tpPrice)) _robot.Stop();
                    break;
                case ActionID.ModifyBuyVolume:
                case ActionID.ModifySellVolume:
                    (positionID, volume) = _systemApi.ReceiveActionModifyVolume();
                    if (!ProcessActionModifyVolume(positionID, volume)) _robot.Stop();
                    break;
                case ActionID.ModifyBuyStopLoss:
                case ActionID.ModifySellStopLoss:
                    (positionID, slPrice) = _systemApi.ReceiveActionModifyStopLoss();
                    if (!ProcessActionModifyStopLoss(positionID, slPrice)) _robot.Stop();
                    break;
                case ActionID.ModifyBuyTakeProfit:
                case ActionID.ModifySellTakeProfit:
                    (positionID, tpPrice) = _systemApi.ReceiveActionModifyTakeProfit();
                    if (!ProcessActionModifyTakeProfit(positionID, tpPrice)) _robot.Stop();
                    break;
                case ActionID.CloseBuy:
                case ActionID.CloseSell:
                    positionID = _systemApi.ReceiveActionClose();
                    if (!ProcessActionClosePosition(positionID)) _robot.Stop();
                    break;
                case ActionID.AskAboveTarget:
                    _lastAskAboveTarget = _systemApi.ReceiveActionAskAboveTarget();
                    break;
                case ActionID.AskBelowTarget:
                    _lastAskBelowTarget = _systemApi.ReceiveActionAskBelowTarget();
                    break;
                case ActionID.BidAboveTarget:
                    _lastBidAboveTarget = _systemApi.ReceiveActionBidAboveTarget();
                    break;
                case ActionID.BidBelowTarget:
                    _lastBidBelowTarget = _systemApi.ReceiveActionBidBelowTarget();
                    break;
                default:
                    _logging.Critical($"Received invalid action ID: {actionID}");
                    throw new ArgumentOutOfRangeException();
            }
        } while (actionID != ActionID.Complete);
    }
}