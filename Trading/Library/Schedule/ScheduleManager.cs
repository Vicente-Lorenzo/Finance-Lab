namespace AlgorithmicTrading.Schedule
{
    public class ScheduleManager
    {
        private readonly TimeSchedule _timeSchedule;
        private readonly ControlSchedule _controlSchedule;

        public ScheduleManager(TimeSchedule timeSchedule, ControlSchedule controlSchedule)
        {
            _timeSchedule = timeSchedule;
            _controlSchedule = controlSchedule;
        }

        public bool IsOnSchedule()
        {
            if (_controlSchedule != null && !_controlSchedule.IsOnSchedule())
                return false;
            if (_timeSchedule != null && !_timeSchedule.IsOnSchedule())
                return false;
            return true;
        }
    }
}