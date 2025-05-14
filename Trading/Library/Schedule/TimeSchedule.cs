using cAlgo.API;

namespace AlgorithmicTrading.Schedule
{
    public class TimeSchedule
    {
        private readonly Robot _robot;

        private readonly int _startHour;
        private readonly int _startMinute;
        private readonly int _stopHour;
        private readonly int _stopMinute;
        
        public TimeSchedule(int startHour, int startMinute, int stopHour, int stopMinute, Robot robot)
        {
            _startHour = startHour;
            _startMinute = startMinute;
            _stopHour = stopHour;
            _stopMinute = stopMinute;
            _robot = robot;
        }

        public bool IsOnSchedule()
        {
            var now = _robot.Time.TimeOfDay;
            var start = new TimeSpan(_startHour, _startMinute, 0);
            var stop = new TimeSpan(_stopHour, _stopMinute, 0);
            if (start < stop)
                return start <= now && now <= stop;
            var midnight1 = new TimeSpan(24, 0, 0);
            var midnight2 = new TimeSpan(0, 0, 0);
            return now >= start && now < midnight1 || now >= midnight2 && now <= stop;
        }
    }
}