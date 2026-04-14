using System;
using System.IO;
using System.IO.Pipes;
using cAlgo.API;

namespace cAlgo.Robots;

public class SystemAPI
{

    private const double Sentinel = -1.0;
    
    private readonly string _iid;
    private readonly string _broker;
    private readonly string _symbol;
    private readonly string _timeframe;
    private readonly Logging _console;
    private NamedPipeServerStream _pipe;

    public SystemAPI(Indicator indicator, string broker, string symbol, string timeframe, Logging.VerboseType console)
    {
        _iid = indicator.InstanceId;
        _broker = broker;
        _symbol = symbol;
        _timeframe = timeframe;
        _console = new Logging(indicator, "API", console);
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

    private static void BuildUpdateID(BinaryWriter writer, IndicatorAPI.UpdateID updateID)
    {
        writer.Write((byte)updateID);
    }

    private static void BuildUpdateRequest(BinaryWriter writer, DateTime dateTime)
    {
        writer.Write(((DateTimeOffset)dateTime).ToUnixTimeMilliseconds());
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
        BuildUpdateID(writer, IndicatorAPI.UpdateID.Complete);
        SendUpdate(memoryStream.ToArray());
    }

    public void SendUpdateRequest(DateTime dateTime)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, IndicatorAPI.UpdateID.Request);
        BuildUpdateRequest(writer, dateTime);
        SendUpdate(memoryStream.ToArray());
    }
    
    public void SendUpdateShutdown()
    {
        using var memoryStream = new MemoryStream();
        using var writer = new BinaryWriter(memoryStream);
        BuildUpdateID(writer, IndicatorAPI.UpdateID.Shutdown);
        SendUpdate(memoryStream.ToArray());
    }

    private byte[] ReceiveAction(int size)
    {
        var buffer = new byte[size];
        _ = _pipe.Read(buffer, 0, buffer.Length);
        return buffer;
    }

    public IndicatorAPI.ActionID ReceiveActionID()
    {
        return (IndicatorAPI.ActionID)ReceiveAction(sizeof(byte))[0];
    }

    public double? ReceiveActionResponse()
    {
        var content = ReceiveAction(sizeof(double));
        var value = BitConverter.ToDouble(content, 0);
        return Math.Abs(value - Sentinel) < double.Epsilon ? null : value;
    }
}