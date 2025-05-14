using cAlgo.API;
using AlgorithmicTrading.Loggers;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.FullAccess)]
    public class Tester : Robot
    {
        [Parameter(DefaultValue = "Hello world!")]
        public string Message { get; set; }

        protected override void OnStart()
        {
            //Telegram telegram = new("2021016289:AAF1wbqMpOyiX1zw2oyO_xWhC5WxIleVJhY", "681929783");
            //Logger logger = new(Logger.VerboseLevel.Debug, this, telegram);
            //logger.Error(Message);
            //logger.Warning(Message);
            //logger.Info(Message);
            //logger.Debug(Message);
            
            Print(Watchlists[1].Name);
        }

        protected override void OnTick()
        {
            // Handle price updates here
        }

        protected override void OnStop()
        {
            // Handle cBot stop here
        }
    }
}