using System;
using System.Collections.Generic;
using cAlgo.API;
using System.Net;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class WebhookRecorder : Robot
    {
        [Parameter("Webhook Url",  Group = "Recorder Settings", DefaultValue = "https://webhookurl.com")]
        public string WebhookUrl { get; set; }
        [Parameter("Record All Trades",  Group = "Recorder Settings", DefaultValue = true)]
        public bool RecordAllTrades { get; set; }

        private Dictionary<int, double?[]> _firstSlTp;

        protected override void OnStart()
        {
            ServicePointManager.Expect100Continue = true;
            ServicePointManager.DefaultConnectionLimit = 1000000;
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;

            _firstSlTp = new Dictionary<int, double?[]>();
            
            Positions.Opened += OnOpenedPosition;
            Positions.Modified += OnModifiedPosition;
            Positions.Closed += OnClosedPosition;
            Print(RecordAllTrades ? "Started recording all trades" : "Started recording trades from this asset");
        }

        private void OnOpenedPosition(PositionOpenedEventArgs args)
        {
            var openedPos = args.Position;
            if (!RecordAllTrades && openedPos.SymbolName != SymbolName)
                return;

            _firstSlTp[openedPos.Id] = new[] { openedPos.StopLoss, openedPos.TakeProfit };
        }

        private void OnModifiedPosition(PositionModifiedEventArgs args)
        {
            var modifiedPos = args.Position;
            if (!RecordAllTrades && modifiedPos.SymbolName != SymbolName)
                return;
            if (!_firstSlTp.ContainsKey(modifiedPos.Id))
                return;
            
            var firstValues = _firstSlTp[modifiedPos.Id];
            if (firstValues[0] == null)
                firstValues[0] = modifiedPos.StopLoss;
            if (firstValues[1] == null)
                firstValues[1] = modifiedPos.TakeProfit;
        }

        private void OnClosedPosition(PositionClosedEventArgs args)
        {
            var closedPos = args.Position;
            if (!RecordAllTrades && closedPos.SymbolName != SymbolName)
                return;

            var pos = History.FindLast(closedPos.Label, closedPos.SymbolName, closedPos.TradeType);
            var content = "";

            AppendContent(ref content, "reason", args.Reason.ToString());
            AppendContent(ref content, "position_id", pos.PositionId.ToString());
            AppendContent(ref content, "deal_id", pos.ClosingDealId.ToString());
            AppendContent(ref content, "symbol", pos.SymbolName);
            AppendContent(ref content, "trade_type", pos.TradeType.ToString());
            
            AppendContent(ref content, "entry_time", pos.EntryTime.ToString());
            AppendContent(ref content, "closing_time", pos.ClosingTime.ToString());
            
            AppendContent(ref content, "entry_price", pos.EntryPrice.ToString());
            AppendContent(ref content, "closing_price", pos.ClosingPrice.ToString());
            
            AppendContent(ref content, "volume", pos.VolumeInUnits.ToString());
            AppendContent(ref content, "quantity", pos.Quantity.ToString());
            
            double firstTpPrice = double.NaN, firstTpPips = double.NaN, firstTpValue = double.NaN, firstSlPrice = double.NaN, firstSlPips = double.NaN, firstSlValue = double.NaN;
            double lastTpPrice = double.NaN, lastTpPips = double.NaN, lastTpValue = double.NaN, lastSlPrice = double.NaN, lastSlPips = double.NaN, lastSlValue = double.NaN;
            var sym = Symbols.GetSymbol(pos.SymbolName);
            
            double?[] firstValues = null;
            if (_firstSlTp.ContainsKey(closedPos.Id))
                firstValues = _firstSlTp[closedPos.Id];

            if (firstValues != null && firstValues[0] != null)
            {
                firstSlPrice = (double)firstValues[0];
                firstSlPips = Math.Round(Math.Abs(firstSlPrice - pos.EntryPrice) / sym.PipSize, 1);
                firstSlValue = Math.Round(-1 * sym.PipValue * firstSlPips * sym.VolumeInUnitsMin, 2);
            }
            
            if (closedPos.StopLoss != null)
            {
                lastSlPrice = (double)closedPos.StopLoss;
                lastSlPips = Math.Round(Math.Abs(lastSlPrice - pos.EntryPrice) / sym.PipSize, 1);
                lastSlValue = Math.Round(-1 * sym.PipValue * lastSlPips * sym.VolumeInUnitsMin, 2);
            }
                
            if (firstValues != null && firstValues[1] != null)
            {
                firstTpPrice = (double)firstValues[1];
                firstTpPips = Math.Round(Math.Abs(firstTpPrice - pos.EntryPrice) / sym.PipSize, 1);
                firstTpValue = Math.Round(sym.PipValue * firstTpPips * sym.VolumeInUnitsMin, 2);
            }
            
            if (closedPos.TakeProfit != null)
            {
                lastTpPrice = (double)closedPos.TakeProfit;
                lastTpPips = Math.Round(Math.Abs(lastTpPrice - pos.EntryPrice) / sym.PipSize, 1);
                lastTpValue = Math.Round(sym.PipValue * lastTpPips * sym.VolumeInUnitsMin, 2);
            }
            
            AppendContent(ref content, "first_tp_price", firstTpPrice.ToString());
            AppendContent(ref content, "first_tp_pips", firstTpPips.ToString());
            AppendContent(ref content, "first_tp_value", firstTpValue.ToString());
            AppendContent(ref content, "first_sl_price", firstSlPrice.ToString());
            AppendContent(ref content, "first_sl_pips", firstSlPips.ToString());
            AppendContent(ref content, "first_sl_value", firstSlValue.ToString());
            AppendContent(ref content, "first_rr_ratio", firstTpPips != double.NaN && firstSlPips != double.NaN ? Math.Round(firstTpPips / firstSlPips, 2).ToString() : double.NaN.ToString());
            
            AppendContent(ref content, "last_tp_price", lastTpPrice.ToString());
            AppendContent(ref content, "last_tp_pips", lastTpPips.ToString());
            AppendContent(ref content, "last_tp_value", lastTpValue.ToString());
            AppendContent(ref content, "last_sl_price", lastSlPrice.ToString());
            AppendContent(ref content, "last_sl_pips", lastSlPips.ToString());
            AppendContent(ref content, "last_sl_value", lastSlValue.ToString());
            AppendContent(ref content, "last_rr_ratio", lastTpPips != double.NaN && lastSlPips != double.NaN ? Math.Round(lastTpPips / lastSlPips, 2).ToString() : double.NaN.ToString());
            
            AppendContent(ref content, "pips", pos.Pips.ToString());
            AppendContent(ref content, "gross_npl", pos.GrossProfit.ToString());
            AppendContent(ref content, "net_npl", pos.NetProfit.ToString());
            AppendContent(ref content, "swap", pos.Swap.ToString());
            AppendContent(ref content, "commission", pos.Commissions.ToString());
            AppendContent(ref content, "balance", pos.Balance.ToString());

            AppendContent(ref content, "trade_duration", (pos.ClosingTime - pos.EntryTime).ToString("hh\\:mm\\:ss"));

            AppendContent(ref content, "label", pos.Label);
            AppendContent(ref content, "comment", pos.Comment);

            _firstSlTp.Remove(closedPos.Id);
            SendPostRequest(content);
        }
        
        private void AppendContent(ref string content, string key, string value)
        {
            value = string.IsNullOrEmpty(value) ? "null" : value;
            if (string.IsNullOrEmpty(content))
                content = key + "=" + value;
            else
                content += "&" + key + "=" + value;
        }

        private void SendPostRequest(string content)
        {
            WebRequest.Create(WebhookUrl + "?" + content).GetResponse();
        }

        protected override void OnStop()
        {
            Print("Stopped recording trades");
        }
    }
}