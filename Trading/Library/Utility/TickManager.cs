using cAlgo.API;

namespace AlgorithmicTrading.Utility
{
    public class TickManager
    {
        public ulong TickCount { get; private set; }
        public TickManager(Robot robot) { robot.Bars.Tick += IncrementTickCounter; }
        private void IncrementTickCounter(BarsTickEventArgs args) { TickCount++; }
    }
}