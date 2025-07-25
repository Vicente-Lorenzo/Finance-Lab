using System;
using System.IO;
using System.IO.Pipes;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots;

public class SystemAPI
{
    private enum AssetType
    {
        USD = 0,
        EUR = 1,
        GBP = 2,
        CAD = 3,
        JPY = 4,
        AUD = 5,
        NZD = 6,
        CHF = 7,
        Other = 8
    }

    private const double Sentinel = -1.0;
    
    private readonly string _iid;
    private readonly string _broker;
    private readonly string _symbol;
    private readonly string _timeframe;
    private readonly Logging _console;
    private NamedPipeServerStream _pipe;

    public SystemAPI(Robot robot, string broker, string symbol, string timeframe, Logging.VerboseType console)
    {
        _iid = robot.InstanceId;
        _broker = broker;
        _symbol = symbol;
        _timeframe = timeframe;
        _console = new Logging(robot, "API", console);
    }

    public void Initialize()
    {
        _pipe = new NamedPipeServerStream(
            pipeName: $@"{_broker}\{_symbol}\{_timeframe}\{_iid}",
            direction: PipeDirection.InOut,
            maxNumberOfServerInstances: 1,
            transmissionMode: PipeTransmissionMode.Byte,
            options: PipeOptions.Asynchronous);
        _console.Info("Pipe initialized");
    }

    public void Connect()
    {
        _pipe.WaitForConnection();
        _console.Info("Connected");
    }

    public void Disconnect()
    {
        if (_pipe is null) return;
        _pipe.Close();
        _pipe.Dispose();
        _console.Info("Disconnected");
    }

    private static void BuildUpdateID(BinaryWriter writer, RobotAPI.UpdateID updateID)
    {
        writer.Write((byte)updateID);
    }

    private static void BuildUpdateAccount(BinaryWriter writer, IAccount account)
    {
        writer.Write((byte)account.AccountType);
        writer.Write((byte)Enum.Parse<AssetType>(account.Asset.Name));
        writer.Write(account.Balance);
        writer.Write(account.Equity);
        writer.Write(account.Credit);
        writer.Write(account.PreciseLeverage);
        writer.Write(account.Margin);
        writer.Write(account.FreeMargin);
        writer.Write(account.MarginLevel ?? Sentinel);
        writer.Write(account.StopOutLevel);
        writer.Write((byte)account.TotalMarginCalculationType);
    }

    private static void BuildUpdateSymbol(BinaryWriter writer, Symbol symbol)
    {
        writer.Write((byte)Enum.Parse<AssetType>(symbol.BaseAsset.Name));
        writer.Write((byte)Enum.Parse<AssetType>(symbol.QuoteAsset.Name));
        writer.Write(symbol.Digits);
        writer.Write(symbol.TickSize);
        writer.Write(symbol.PipSize);
        writer.Write(symbol.LotSize);
        writer.Write(symbol.VolumeInUnitsMin);
        writer.Write(symbol.VolumeInUnitsMax);
        writer.Write(symbol.VolumeInUnitsStep);
        writer.Write(symbol.Commission);
        writer.Write((byte)symbol.CommissionType);
        writer.Write(symbol.SwapLong);
        writer.Write(symbol.SwapShort);
        writer.Write((byte)symbol.SwapCalculationType);
        writer.Write((sbyte?)symbol.Swap3DaysRollover ?? (sbyte)Sentinel);
    }

    private static void BuildUpdatePosition(BinaryWriter writer, Symbol symbol, Position position)
    {
        writer.Write(position.Id);
        writer.Write((byte)Enum.Parse<RobotAPI.PositionType>(position.Comment));
        writer.Write((byte)position.TradeType);
        writer.Write(((DateTimeOffset)position.EntryTime).ToUnixTimeMilliseconds());
        writer.Write(position.EntryPrice);
        writer.Write(position.VolumeInUnits);
        writer.Write(position.Quantity);
        writer.Write(position.Pips * symbol.PipSize / symbol.TickSize);
        writer.Write(position.Pips);
        writer.Write(position.GrossProfit);
        writer.Write(position.Commissions);
        writer.Write(position.Swap);
        writer.Write(position.NetProfit);
        writer.Write(position.StopLoss ?? Sentinel);
        writer.Write(position.TakeProfit ?? Sentinel);
        writer.Write(position.Margin);
    }

    private static void BuildUpdateTrade(BinaryWriter writer, Symbol symbol, HistoricalTrade trade)
    {
        writer.Write(trade.PositionId);
        writer.Write(trade.ClosingDealId);
        writer.Write((byte)Enum.Parse<RobotAPI.PositionType>(trade.Comment));
        writer.Write((byte)trade.TradeType);
        writer.Write(((DateTimeOffset)trade.EntryTime).ToUnixTimeMilliseconds());
        writer.Write(((DateTimeOffset)trade.ClosingTime).ToUnixTimeMilliseconds());
        writer.Write(trade.EntryPrice);
        writer.Write(trade.ClosingPrice);
        writer.Write(trade.VolumeInUnits);
        writer.Write(trade.Quantity);
        writer.Write(trade.Pips * symbol.PipSize / symbol.TickSize);
        writer.Write(trade.Pips);
        writer.Write(trade.GrossProfit);
        writer.Write(trade.Commissions);
        writer.Write(trade.Swap);
        writer.Write(trade.NetProfit);
    }

    private static void BuildUpdateBar(BinaryWriter writer, Bar bar)
    {
        writer.Write(((DateTimeOffset)bar.OpenTime).ToUnixTimeMilliseconds());
        writer.Write(bar.Open);
        writer.Write(bar.High);
        writer.Write(bar.Low);
        writer.Write(bar.Close);
        writer.Write(bar.TickVolume);
    }

    private static void BuildUpdateTick(BinaryWriter writer, DateTime tickTime, double ask, double bid)
    {
        writer.Write(((DateTimeOffset)tickTime).ToUnixTimeMilliseconds());
        writer.Write(ask);
        writer.Write(bid);
    }
    
    private void SendUpdate(byte[] message)
    {
        _pipe.Write(message, 0, message.Length);
        _pipe.Flush();
    }

    public void SendUpdateComplete()
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, RobotAPI.UpdateID.Complete);
        SendUpdate(memoryStream.ToArray());
    }

    public void SendUpdateAccount(IAccount account)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, RobotAPI.UpdateID.Account);
        BuildUpdateAccount(writer, account);
        SendUpdate(memoryStream.ToArray());
    }

    public void SendUpdateSymbol(Symbol symbol)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, RobotAPI.UpdateID.Symbol);
        BuildUpdateSymbol(writer, symbol);
        SendUpdate(memoryStream.ToArray());
    }

    private void SendUpdatePosition(RobotAPI.UpdateID updateID, Bar bar, IAccount account, Symbol symbol, Position position)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, updateID);
        BuildUpdateBar(writer, bar);
        BuildUpdateAccount(writer, account);
        BuildUpdatePosition(writer, symbol, position);
        SendUpdate(memoryStream.ToArray());
    }

    private void SendUpdateTrade(RobotAPI.UpdateID updateID, Bar bar, IAccount account, Symbol symbol, HistoricalTrade trade)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, updateID);
        BuildUpdateBar(writer, bar);
        BuildUpdateAccount(writer, account);
        BuildUpdateTrade(writer, symbol, trade);
        SendUpdate(memoryStream.ToArray());
    }

    private void SendUpdatePositionTrade(RobotAPI.UpdateID updateID, Bar bar, IAccount account, Symbol symbol, Position position, HistoricalTrade trade)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, updateID);
        BuildUpdateBar(writer, bar);
        BuildUpdateAccount(writer, account);
        BuildUpdatePosition(writer, symbol, position);
        BuildUpdateTrade(writer, symbol, trade);
        SendUpdate(memoryStream.ToArray());
    }

    public void SendUpdateOpenedBuy(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.OpenedBuy, bar, account, symbol, position); }
    public void SendUpdateOpenedSell(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.OpenedSell, bar, account, symbol, position); }
    public void SendUpdateModifiedBuyVolume(Bar bar, IAccount account, Symbol symbol, Position position, HistoricalTrade trade) { SendUpdatePositionTrade(RobotAPI.UpdateID.ModifiedBuyVolume, bar, account, symbol, position, trade); }
    public void SendUpdateModifiedBuyStopLoss(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.ModifiedBuyStopLoss, bar, account, symbol, position); }
    public void SendUpdateModifiedBuyTakeProfit(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.ModifiedBuyTakeProfit, bar, account, symbol, position); }
    public void SendUpdateModifiedSellVolume(Bar bar, IAccount account, Symbol symbol, Position position, HistoricalTrade trade) { SendUpdatePositionTrade(RobotAPI.UpdateID.ModifiedSellVolume, bar, account, symbol, position, trade); }
    public void SendUpdateModifiedSellStopLoss(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.ModifiedSellStopLoss, bar, account, symbol, position); }
    public void SendUpdateModifiedSellTakeProfit(Bar bar, IAccount account, Symbol symbol, Position position) { SendUpdatePosition(RobotAPI.UpdateID.ModifiedSellTakeProfit, bar, account, symbol, position); }
    public void SendUpdateClosedBuy(Bar bar, IAccount account, Symbol symbol, HistoricalTrade trade) { SendUpdateTrade(RobotAPI.UpdateID.ClosedBuy, bar, account, symbol, trade); }
    public void SendUpdateClosedSell(Bar bar, IAccount account, Symbol symbol, HistoricalTrade trade) { SendUpdateTrade(RobotAPI.UpdateID.ClosedSell, bar, account, symbol, trade); }
    
    public void SendUpdateBarClosed(Bar bar)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, RobotAPI.UpdateID.BarClosed);
        BuildUpdateBar(writer, bar);
        SendUpdate(memoryStream.ToArray());
    }

    private void SendUpdateTarget(DateTime tickTime, RobotAPI.UpdateID targetType, double ask, double bid)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, targetType);
        BuildUpdateTick(writer, tickTime, ask, bid);
        SendUpdate(memoryStream.ToArray());
    }

    public void SendUpdateAskAboveTarget(DateTime tickTime, double ask, double bid) { SendUpdateTarget(tickTime, RobotAPI.UpdateID.AskAboveTarget, ask, bid); }
    public void SendUpdateAskBelowTarget(DateTime tickTime, double ask, double bid) { SendUpdateTarget(tickTime, RobotAPI.UpdateID.AskBelowTarget, ask, bid); }
    public void SendUpdateBidAboveTarget(DateTime tickTime, double ask, double bid) { SendUpdateTarget(tickTime, RobotAPI.UpdateID.BidAboveTarget, ask, bid); }
    public void SendUpdateBidBelowTarget(DateTime tickTime, double ask, double bid) { SendUpdateTarget(tickTime, RobotAPI.UpdateID.BidBelowTarget, ask, bid); }
    
    public void SendUpdateShutdown()
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, RobotAPI.UpdateID.Shutdown);
        SendUpdate(memoryStream.ToArray());
    }

    private byte[] ReceiveAction(int size)
    {
        var buffer = new byte[size];
        _ = _pipe.Read(buffer, 0, buffer.Length);
        return buffer;
    }

    public RobotAPI.ActionID ReceiveActionID()
    {
        return (RobotAPI.ActionID)ReceiveAction(sizeof(byte))[0];
    }

    public (RobotAPI.PositionType, double, double?, double?) ReceiveActionOpen()
    {
        var content = ReceiveAction(sizeof(byte) + 3 * sizeof(double));
        var posType = (RobotAPI.PositionType)content[0];
        var volume = BitConverter.ToDouble(content, sizeof(byte));
        var slAux = BitConverter.ToDouble(content, sizeof(byte) + 1 * sizeof(double));
        var tpAux = BitConverter.ToDouble(content, sizeof(byte) + 2 * sizeof(double));
        double? slPips = Math.Abs(slAux - Sentinel) < double.Epsilon ? null : slAux;
        double? tpPips = Math.Abs(tpAux - Sentinel) < double.Epsilon ? null : tpAux;
        return (posType, volume, slPips, tpPips);
    }

    public (int, double) ReceiveActionModifyVolume()
    {
        var content = ReceiveAction(sizeof(int) + sizeof(double));
        var positionID = BitConverter.ToInt32(content, 0);
        var volume = BitConverter.ToDouble(content, 1 * sizeof(int));
        return (positionID, volume);
    }

    private (int, double?) ReceiveActionModifyLimit()
    {
        var content = ReceiveAction(sizeof(int) + sizeof(double));
        var positionID = BitConverter.ToInt32(content, 0);
        var limit = BitConverter.ToDouble(content, sizeof(int));
        return (positionID, Math.Abs(limit - Sentinel) < double.Epsilon ? null : limit);
    }
    
    public (int, double?) ReceiveActionModifyStopLoss() { return ReceiveActionModifyLimit(); }
    public (int, double?) ReceiveActionModifyTakeProfit() { return ReceiveActionModifyLimit(); }

    public int ReceiveActionClose()
    {
        var content = ReceiveAction(sizeof(int));
        var positionID = BitConverter.ToInt32(content, 0);
        return positionID;
    }

    private double? ReceiveActionTarget()
    {
        var content = ReceiveAction(sizeof(double));
        var target = BitConverter.ToDouble(content, 0);
        return Math.Abs(target - Sentinel) < double.Epsilon ? null : target;
    }
    
    public double? ReceiveActionAskAboveTarget() { return ReceiveActionTarget(); }
    public double? ReceiveActionAskBelowTarget() { return ReceiveActionTarget(); }
    public double? ReceiveActionBidAboveTarget() { return ReceiveActionTarget(); }
    public double? ReceiveActionBidBelowTarget() { return ReceiveActionTarget(); }
}