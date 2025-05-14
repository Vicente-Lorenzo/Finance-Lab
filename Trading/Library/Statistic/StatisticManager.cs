using cAlgo.API;
using AlgorithmicTrading.Utility;

namespace AlgorithmicTrading.Statistics
{
    public class StatisticManager
    {
        // Statistics attributes
        public int TotalTrades;
        public int TotalWinners;
        public int TotalLosers;
        public double BiggestLoserNpl;
        public double BiggestWinnerNpl;
        public double MaxLosingStreak;
        public double MaxWinningStreak;
        public double CostsInCommissions;
        
        // Auxiliary Statistics attributes
        private double _totalWinnersNpl;
        private double _totalLosersNpl;
        private double _currentLosingStreak;
        private double _currentWinningStreak;
        private TimeSpan _totalHoldingTime;

        // Other attributes
        private readonly Robot _robot;

        // Statistics Group and Control attributes
        private readonly string _statisticsGroupLabel;
        private readonly Dictionary<int, TempStatistics> _temporaryStatistics;

        public StatisticManager(string statisticsId, Robot robot)
        {
            _statisticsGroupLabel = LabelManager.BuildStatisticsGroupLabel(statisticsId);
            _robot = robot;
            _temporaryStatistics = new Dictionary<int, TempStatistics>();
            
            _robot.Positions.Opened += PositionOpenedEventCallback;
            _robot.Positions.Closed += PositionClosedEventCallback;
            _robot.Positions.Modified += PositionModifiedEventCallback;
        }

        // Callback called when a position is opened. Verifies if it is part of the statistics group and, if so, starts analysing it
        private void PositionOpenedEventCallback(PositionOpenedEventArgs args)
        {
            var openedPos = args.Position;
            if (openedPos.Label != null && openedPos.Label.Contains(_statisticsGroupLabel))
                _temporaryStatistics[openedPos.Id] = new TempStatistics(0.0, openedPos.VolumeInUnits);
        }

        // Callback called when a position is modified. Verifies if it is a registered position and, if so, analyzes it
        private void PositionModifiedEventCallback(PositionModifiedEventArgs args)
        {
            var modifiedPos = args.Position;
            if (!_temporaryStatistics.TryGetValue(modifiedPos.Id, out var tempStats) || Math.Abs(tempStats.LastVolume - modifiedPos.VolumeInUnits) < double.Epsilon) 
                return;
            var histPos = _robot.History.FindLast(modifiedPos.Label, modifiedPos.SymbolName, modifiedPos.TradeType);
            tempStats.TotalNpl += histPos.NetProfit;
            tempStats.LastVolume = modifiedPos.VolumeInUnits;
            CostsInCommissions += histPos.Commissions;
        }

        // Callback called when a position is closed. Verifies if it is a registered position and, if so, analyzes it
        private void PositionClosedEventCallback(PositionClosedEventArgs args)
        {
            var closedPos = args.Position;
            if (!_temporaryStatistics.TryGetValue(closedPos.Id, out var tempStats)) 
                return;
            var histPos = _robot.History.FindLast(closedPos.Label, closedPos.SymbolName, closedPos.TradeType);
            tempStats.TotalNpl += closedPos.NetProfit;
            if (tempStats.TotalNpl >= 0)
            {
                TotalTrades++;
                TotalWinners++;
                _totalWinnersNpl += tempStats.TotalNpl;
                BiggestWinnerNpl = Math.Max(BiggestWinnerNpl, tempStats.TotalNpl);
                _currentLosingStreak = 0;
                MaxWinningStreak = Math.Max(MaxWinningStreak, ++_currentWinningStreak);
            }
            else
            {
                TotalTrades++;
                TotalLosers++;
                _totalLosersNpl += tempStats.TotalNpl;
                BiggestLoserNpl = Math.Min(BiggestLoserNpl, tempStats.TotalNpl);
                _currentWinningStreak = 0;
                MaxLosingStreak = Math.Max(MaxLosingStreak, ++_currentLosingStreak);
            }
            CostsInCommissions += histPos.Commissions;
            _totalHoldingTime += _robot.Time - closedPos.EntryTime;
            _temporaryStatistics.Remove(closedPos.Id);
        }

        // Auxiliary method to calculate ratios
        private static double CalculateRatio(double numerator, double denominator) { return denominator == 0 ? double.PositiveInfinity : numerator / denominator; }
        
        // Auxiliary method to calculate percentages from ratios
        private static double CalculatePercentage(double ratio) { return Math.Round(ratio * 100, 2); }
        
        // Net profit/loss of the trading session
        public double CalculateNetProfitLoss() { return Math.Round(_totalWinnersNpl + _totalLosersNpl, 2); }

        // Ratio of winners vs losers
        public double CalculateWinnersRatio() { return CalculateRatio(TotalWinners, TotalTrades); }

        // Ratio of losers vs winners
        public double CalculateLosersRatio() { return CalculateRatio(TotalLosers, TotalTrades); }

        // Ratio of winners vs losers in percentage
        public static double CalculateWinnersPercentage(double winningRatio) { return CalculatePercentage(winningRatio); }

        // Ratio of losers vs winners in percentage
        public static double CalculateLosersPercentage(double losingRatio) { return CalculatePercentage(losingRatio); }

        // Average amount that you win per winning trade
        public double CalculateAverageWinner() { return Math.Round(_totalWinnersNpl / TotalWinners, 2); }

        // Average amount that you lose per loser trade
        public double CalculateAverageLoser() { return Math.Round(_totalLosersNpl / TotalLosers, 2); }
        
        // Expected amount to earn or lose on a trade
        public static double CalculateExpectedValue(double winRatio, double averageWinner, double loseRatio, double averageLoser) { return Math.Round(winRatio * averageWinner + loseRatio * averageLoser, 2); }

        // Determine how robust a trading strategy is
        public static double CalculateExpectationValue(double expectedValue, double averageLoser) { return Math.Round(expectedValue / Math.Abs(averageLoser), 2); }

        // Calculate the average holding time
        public string CalculateAverageHoldingTime() 
        {
            var timeSpan = TimeSpan.FromMilliseconds(_totalHoldingTime.TotalMilliseconds/TotalTrades);
            return $"{timeSpan.Days} Days {timeSpan.Hours} Hours {timeSpan.Minutes} Minutes";
        }
    }

    internal class TempStatistics
    {
        internal double TotalNpl;
        internal double LastVolume;

        internal TempStatistics(double totalNpl, double lastVolume)
        {
            TotalNpl = totalNpl;
            LastVolume = lastVolume;
        }
    }
}