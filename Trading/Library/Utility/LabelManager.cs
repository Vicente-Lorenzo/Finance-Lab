namespace AlgorithmicTrading.Utility
{
    public static class LabelManager
    {
        private const string ManagerGroupLabel = "M";
        private const string StatisticsGroupLabel = "S";

        public static string BuildManagerGroupLabel(string managerId, string symbolId, string timeframeId)
        {
            return $"{ManagerGroupLabel}={managerId}{symbolId}{timeframeId}";
        }

        public static string BuildStatisticsGroupLabel(string statisticsId)
        {
            return $"{StatisticsGroupLabel}={statisticsId}";
        }

        public static string BuildUniqueLabel(string managerId, string symbolId, string timeframeId, string statisticsId)
        {
            return $"{BuildManagerGroupLabel(managerId, symbolId, timeframeId)}|{BuildStatisticsGroupLabel(statisticsId)}";
        }
    }
}