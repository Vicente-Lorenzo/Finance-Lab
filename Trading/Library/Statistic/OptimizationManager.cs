using cAlgo.API;
using PdfSharp.Pdf;
using PdfSharp.Drawing;
using PdfSharp.Charting;
using AlgorithmicTrading.Utility;

namespace AlgorithmicTrading.Statistics
{
    public class OptimizationManager
    {
        // Optimization Trust Value
        public enum OptimizationTrustLevel { Low, Medium, High }
        
        // Optimization Information attributes
        private readonly double _initialBalance;
        private readonly string _brokerName;
        private readonly DateTime _initialTime;
        private DateTime _finalTime;
        
        // Other attributes
        private readonly StatisticManager _statisticsManager;
        private readonly List<IndicatorInformation> _indicatorsInformation;
        private readonly Robot _robot;

        public OptimizationManager(StatisticManager statisticsManager, Robot robot)
        {
            _statisticsManager = statisticsManager;
            _indicatorsInformation = new List<IndicatorInformation>();
            _robot = robot;

            _initialBalance = _robot.Account.Balance;
            _brokerName = _robot.Account.BrokerName;
            _initialTime = _robot.Time;
        }
        
        public void AddIndicatorInformation(string indicatorName, string indicatorFunction, string[] indicatorParams)
        {
            _indicatorsInformation.Add(new IndicatorInformation(indicatorName, indicatorFunction, indicatorParams));
        }
        
        public double CalculateFitnessValue(GetFitnessArgs args)
        {
            _finalTime = _robot.Time;
            var result = Math.Abs(args.NetProfit * args.SharpeRatio) * (1 - args.MaxEquityDrawdownPercentages / 100);
            return args.NetProfit < 0 || args.SharpeRatio < 0 ? -1 * result : result;
        }

        public void SaveOptimization(GetFitnessArgs args, OptimizationTrustLevel trustLevel)
        {
            // Create the pdf
            var document = new PdfDocument();
            var summaryPage = document.AddPage();
            var summaryGfx = XGraphics.FromPdfPage(summaryPage);
            
            // Define the Fonts
            var mainTitleFont = new XFont("Consolas", 16, XFontStyle.Bold);
            var titleFont = new XFont("Consolas", 12, XFontStyle.Underline);
            var normalFont = new XFont("Consolas", 12, XFontStyle.Regular);

            const int pageSpace = 30;
            const int midPageSpace = 244;
            const int endPageSpace = 458;
            const int posTitleSpace = 25;
            const int lineSpace = 20;
            var currentLine = 0;

            // Draw the Main Title
            currentLine += pageSpace;
            summaryGfx.DrawString("Optimization Report - " + DateTime.Now.ToString("dd-MM-yyyy hh:mm"), mainTitleFont, XBrushes.Black, new XRect(0, pageSpace, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopCenter);
            currentLine += pageSpace;
            
            // Draw the General Section
            summaryGfx.DrawString("General Information", titleFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += posTitleSpace;
            summaryGfx.DrawString("Broker: " + _brokerName, normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Asset: {_robot.SymbolName} ({_robot.TimeFrame})", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Trust: " + trustLevel, normalFont, XBrushes.Black, new XRect(endPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString("Start: " + _initialTime.ToString("dd-MM-yyyy"), normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Stop: " + _finalTime.ToString("dd-MM-yyyy"), normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Duration: {(_finalTime - _initialTime).Days} Days" , normalFont, XBrushes.Black, new XRect(endPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += pageSpace;
            
            // Draw the Indicator Section
            summaryGfx.DrawString("Indicators and Parameters", titleFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += posTitleSpace;
            foreach (var indicator in _indicatorsInformation)
            {
                summaryGfx.DrawString(indicator.IndicatorName, normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
                summaryGfx.DrawString($"({indicator.IndicatorFunction})", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
                var text = "";
                foreach (var parameter in indicator.IndicatorParams)
                    text += " " + parameter;
                summaryGfx.DrawString(text, normalFont, XBrushes.Black, new XRect(-pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopRight);
                currentLine += lineSpace;
            }
            currentLine -= lineSpace;
            currentLine += pageSpace;
            
            // Draw the Statistics Section
            var winningRatio = _statisticsManager.CalculateWinnersRatio();
            var losingRatio = _statisticsManager.CalculateLosersRatio();
            var averageWinning = _statisticsManager.CalculateAverageWinner();
            var averageLosing = _statisticsManager.CalculateAverageLoser();
            var expectedValue = StatisticManager.CalculateExpectedValue(winningRatio, averageWinning, losingRatio, averageLosing);
            var expectationValue = StatisticManager.CalculateExpectationValue(expectedValue, averageLosing);
            
            summaryGfx.DrawString("Performance and Statistics", titleFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += posTitleSpace;
            summaryGfx.DrawString($"Initial Balance: {Math.Round(_initialBalance, 2)}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Total Trades: " + _statisticsManager.TotalTrades, normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Net Profit/Loss: {_statisticsManager.CalculateNetProfitLoss()}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Winning Trades: {_statisticsManager.TotalWinners} ({Math.Round(StatisticManager.CalculateWinnersPercentage(winningRatio), 2)}%)", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Costs in Commissions: {Math.Round(_statisticsManager.CostsInCommissions, 2)}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Losing Trades: {_statisticsManager.TotalLosers} ({StatisticManager.CalculateLosersPercentage(losingRatio)}%)", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            currentLine += lineSpace;
            
            summaryGfx.DrawString($"Expected Value: {expectedValue}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Expectation Value: " + expectationValue, normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Avg. Winning Trade: {averageWinning}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Profit Factor: " + args.ProfitFactor, normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Avg. Losing Trade: {averageLosing}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Sharpe Ratio: " + Math.Round(args.SharpeRatio, 3), normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString("Max. Winning Streak: " + _statisticsManager.MaxWinningStreak, normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Sortino Ratio: " + Math.Round(args.SortinoRatio, 3), normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString("Max. Losing Streak: " + _statisticsManager.MaxLosingStreak, normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Max. Balance Drawdown: {Math.Round(args.MaxBalanceDrawdown, 2)}€ ({Math.Round(args.MaxBalanceDrawdownPercentages, 2)}%)", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Best Winning Trade: {Math.Round(_statisticsManager.BiggestWinnerNpl, 2)}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString($"Max. Equity Drawdown: {Math.Round(args.MaxEquityDrawdown, 2)}€ ({Math.Round(args.MaxEquityDrawdownPercentages, 2)}%)", normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += lineSpace;
            summaryGfx.DrawString($"Worst Losing Trade: {Math.Round(_statisticsManager.BiggestLoserNpl, 2)}€", normalFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            summaryGfx.DrawString("Avg. Holding Time: " + _statisticsManager.CalculateAverageHoldingTime(), normalFont, XBrushes.Black, new XRect(midPageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += pageSpace;
            
            // Draw the Performance Chart Title
            summaryGfx.DrawString("Performance Chart", titleFont, XBrushes.Black, new XRect(pageSpace, currentLine, summaryPage.Width.Point, summaryPage.Height.Point), XStringFormats.TopLeft);
            currentLine += posTitleSpace;
            
            var miniChart = new PdfSharp.Charting.Chart(PdfSharp.Charting.ChartType.Line);

            miniChart.Font.Name = "Consolas";
            miniChart.Font.Size = 9;

            miniChart.YAxis.Title.Caption = "";
            miniChart.YAxis.MajorGridlines.LineFormat.Visible = true;
            miniChart.YAxis.MajorGridlines.LineFormat.DashStyle = XDashStyle.Solid;
            miniChart.YAxis.MajorTickMark = TickMarkType.None;
            miniChart.YAxis.MinorTickMark = TickMarkType.None;
            miniChart.XAxis.Title.Caption = "";

            miniChart.PlotArea.LineFormat.Color = XColors.Black;
            miniChart.PlotArea.LineFormat.Width = 1;
            miniChart.PlotArea.LineFormat.Visible = true;
            
            var miniYAxis = miniChart.SeriesCollection.AddSeries();
            miniYAxis.MarkerStyle = MarkerStyle.None;
            var miniXAxis = miniChart.XValues.AddXSeries();
            var nplOverTime = 0.0;
            miniYAxis.Add(nplOverTime);
            foreach (var histPosition in args.History)
            {
                nplOverTime += histPosition.NetProfit;
                miniYAxis.Add(nplOverTime);
            }
            miniXAxis.Add("0");
            int total = args.History.Count, step = total > 10 ? total / 10 : 1;
            for (int i = 1, nextIndexToDraw = step; i < total; i++)
            {
                if (i == nextIndexToDraw)
                {
                    miniXAxis.Add(i.ToString());
                    nextIndexToDraw += step;
                    continue;
                }
                miniXAxis.AddBlank();
            }
            miniXAxis.Add(total.ToString());
            
            var miniChartFrame = new ChartFrame(new XRect(pageSpace, currentLine, summaryPage.Width.Point - 2 * pageSpace, summaryPage.Height.Point - currentLine - pageSpace));
            miniChartFrame.Add(miniChart);
            miniChartFrame.Draw(summaryGfx);
            
            // Save the pdf
            var pdfFilePath = FileManager.BuildOptimizationFileName(_robot.Symbol, _robot.TimeFrame, DateTime.Now.ToString("dd-MM-yyyy_hh-mm-ss"));
            FileManager.CreateDirectory(pdfFilePath);
            document.Save(pdfFilePath);
            document.Close();
        }
    }
    
    internal struct IndicatorInformation
    {
        internal readonly string IndicatorName;
        internal readonly string IndicatorFunction;
        internal readonly string[] IndicatorParams;

        internal IndicatorInformation(string indicatorName, string indicatorFunction, string[] indicatorParams)
        {
            IndicatorName = indicatorName;
            IndicatorFunction = indicatorFunction;
            IndicatorParams = indicatorParams;
        }
    }
}