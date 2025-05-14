using cAlgo.API;
using AlgorithmicTrading.Loggers;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.Internet)]
    public class TelegramAlerts : Robot
    {
        [Parameter("Bot Token", Group = "Telegram Settings", DefaultValue = "INSERT TOKEN HERE")]
        public string BotToken { get; set; }
        [Parameter("Chat ID", Group = "Telegram Settings", DefaultValue = "INSERT CHAT ID HERE")]
        public string ChatId { get; set; }

        [Parameter("Opened Positions", Group = "Alert Settings", DefaultValue = true)]
        public bool AlertOpenedPositions { get; set; }
        [Parameter("Modified Positions", Group = "Alert Settings", DefaultValue = true)]
        public bool AlertModifiedPositions { get; set; }
        [Parameter("Closed Positions", Group = "Alert Settings", DefaultValue = true)]
        public bool AlertClosedPositions { get; set; }

        private Telegram _telegram;

        protected override void OnStart()
        {
            _telegram = new Telegram(BotToken, ChatId);
            if (AlertOpenedPositions)
                Positions.Opened += OpenedPositionCallback;
            if (AlertModifiedPositions)
                Positions.Modified += ModifiedPositionCallback;
            if (AlertClosedPositions)
                Positions.Closed += ClosedPositionCallback;
        }

        private void OpenedPositionCallback(PositionOpenedEventArgs args)
        {
            var pos = args.Position;
            var message = string.Format("[{0}] Position Opened!\nId: {1}\nEntry Time: {2}\nDirection: {3}\nLots: {4}\nEntry Price: {5}\nStop-Loss: {6}\nTake-Profit:{7}",
                pos.SymbolName, pos.Id, pos.EntryTime, pos.TradeType, pos.Quantity, pos.EntryPrice, pos.StopLoss, pos.TakeProfit);
            _telegram.SendText(message);
        }

        private void ModifiedPositionCallback(PositionModifiedEventArgs args)
        {
            var pos = args.Position;
            var message = string.Format("[{0}] Position Modified!\nId: {1}\nEntry Time: {2}\nDirection: {3}\nLots: {4}\nEntry Price: {5}\nStop-Loss: {6}\nTake-Profit:{7}",
                pos.SymbolName, pos.Id, pos.EntryTime, pos.TradeType, pos.Quantity, pos.EntryPrice, pos.StopLoss, pos.TakeProfit);
            _telegram.SendText(message);
        }

        private void ClosedPositionCallback(PositionClosedEventArgs args)
        {
            var pos = args.Position;
            var message = string.Format("[{0}] Position Closed!\nId: {1}\nEntry Time: {2}\nDirection: {3}\nLots: {4}\nEntry Price: {5}\nStop-Loss: {6}\nTake-Profit:{7}\nPips:{8}\nGross Profit: {9}\nCommissions: {10}\nSwaps: {11}\nNet Profit: {12}",
                pos.SymbolName, pos.Id, pos.EntryTime, pos.TradeType, pos.Quantity, pos.EntryPrice, pos.StopLoss, pos.TakeProfit, pos.Pips, pos.GrossProfit, pos.Commissions, pos.Swap, pos.NetProfit);
            _telegram.SendText(message);
        }

    }
}