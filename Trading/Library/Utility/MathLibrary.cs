using cAlgo.API;

namespace AlgorithmicTrading.Utility
{
    public static class MathLibrary
    {
        // Convert pips into a difference of price. May receive negative, positive and 0 pips
        public static double ConvertPipsToDeltaPrice(double pips, double pipSize)
        {
            return pips * pipSize;
        }

        // Convert a difference in price to pips. May receive negative, positive and 0 deltaprice
        public static double ConvertDeltaPriceToPips(double deltaPrice, double pipSize)
        {
            return Math.Round(deltaPrice / pipSize, 1);
        }

        // Returns the position stop-loss in pips. If the position is closed or has no stoploss returns null
        public static double? CalculateStopLossPips(cAlgo.API.Position position, double pipSize)
        {
            if (position.StopLoss == null)
                return null;

            return ConvertDeltaPriceToPips(position.TradeType == TradeType.Buy
                ? (double) position.StopLoss - position.EntryPrice
                : position.EntryPrice - (double) position.StopLoss, pipSize);
        }

        // Returns the position take-profit in pips. If the position is closed or has no takeprofit returns null
        public static double? CalculateTakeProfitPips(cAlgo.API.Position position, double pipSize)
        {
            if (position.TakeProfit == null)
                return null;

            return ConvertDeltaPriceToPips(position.TradeType == TradeType.Buy
                ? (double) position.TakeProfit - position.EntryPrice
                : position.EntryPrice - (double) position.TakeProfit, pipSize);
        }

        // Calculates the volume needed to risk a certain amount of balance having in consideration the stoploss. Assumes the arguments are correct
        public static double CalculateVolumeByRisk(double riskPerc, double slPips, double balance, double pipValue)
        {
            return balance * riskPerc / 100 / (pipValue * slPips);
        }

        // Calculates the risk at stake for a certain amount of volume having in consideration the stoploss. Assumes the arguments are correct
        public static double CalculateRiskByVolume(double? slPips, double volumeAtRisk, double balance, double pipValue)
        {
            // If no stoploss is found the risk is 100%
            if (slPips == null)
                return 100;
            // If the stoploss is positive the risk is 0%
            if (slPips >= 0.0)
                return 0;
            return Math.Round(volumeAtRisk * pipValue * Math.Abs((double) slPips) / balance * 100, 2);
        }

        // Calculates the volume percentage from the initial volume for the volume given. Assumes the argument is correct
        public static double CalculatePercentageByVolume(double volume, double totalVolume)
        {
            return Math.Round(volume / totalVolume * 100, 2);
        }

        // Calculate the volume using the given percentage. Assumes the argument is correct
        public static double CalculateVolumeByPercentage(double riskPerc, double totalVolume)
        {
            return totalVolume * (riskPerc / 100);
        }
    }
}