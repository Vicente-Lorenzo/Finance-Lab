using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;
using cAlgo.Indicators;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class MultipleEntriesScript : Robot
    {
        [Parameter("Number of Trades", Group = "Position Settings", DefaultValue = 5, MinValue = 1)]
        public int NumberOfTrades { get; set; }
        [Parameter("Volume (Lots)", Group = "Position Settings", DefaultValue = 0.1, MinValue = 0.01, Step = 0.01)]
        public double StaticVolumeLots { get; set; }
        [Parameter("Stop-Loss (Pips)", Group = "Position Settings", DefaultValue = 20.0, MinValue = 0.1)]
        public double StopLossPips { get; set; }
        [Parameter("Take-Profit (Pips)", Group = "Position Settings", DefaultValue = 40.0, MinValue = 0.1)]
        public double TakeProfitPips { get; set; }

        protected override void OnStart()
        {
            var panel = new WrapPanel()
            {
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top,
            };
            var button = new Button
            {
                Text = "Buy",
                Margin = 5,
                BackgroundColor = Color.RoyalBlue,
                Height = 61,
                Width = 100,
                FontSize = 20,
            };
            button.Click += BuyButtonClick;
            panel.AddChild(button);
            button = new Button
            {
                Text = "Sell",
                Margin = 5,
                BackgroundColor = Color.IndianRed,
                Height = 61,
                Width = 100,
                FontSize = 20
            };
            button.Click += SellButtonClick;
            panel.AddChild(button);
            Chart.AddControl(panel);
            
            panel = new WrapPanel()
            {
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Bottom,
            };
            button = new Button
            {
                Text = "Close All",
                Margin = 5,
                BackgroundColor = Color.Gray,
                Height = 61,
                Width = 205,
                FontSize = 20
            };
            button.Click += CloseAllButtonClick;
            panel.AddChild(button);
            Chart.AddControl(panel);
        }
        
        private void BuyButtonClick(ButtonClickEventArgs obj)
        {
            for (var i = 0; i < NumberOfTrades; i++)
            {
                ExecuteMarketOrder(TradeType.Buy, SymbolName, StaticVolumeLots * Symbol.LotSize, "BUY_" + i + Time, StopLossPips, TakeProfitPips);
            }
        }

        private void SellButtonClick(ButtonClickEventArgs obj)
        {
            for (var i = 0; i < NumberOfTrades; i++)
            {
                ExecuteMarketOrder(TradeType.Sell, SymbolName, StaticVolumeLots * Symbol.LotSize, "SELL_" + i + Time, StopLossPips, TakeProfitPips);
            }
        }
        
        private void CloseAllButtonClick(ButtonClickEventArgs obj)
        {
            foreach (var pos in Positions)
            {
                pos.Close();
            }
        }
    }
}