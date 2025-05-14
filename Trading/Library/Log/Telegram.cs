namespace AlgorithmicTrading.Log
{
    public class Telegram
    {
        private readonly HttpClient _client;
        private readonly string _defaultUri;

        public Telegram(string token, string defaultChatId)
        {
            _client = new();
            _defaultUri = $"https://api.telegram.org/bot{token}/sendMessage?chat_id={defaultChatId}&text=";
        }

        public void SendText(string message)
        {
            _client.PostAsync(_defaultUri + message, null);
        }
        
        // Default Token = 2021016289:AAF1wbqMpOyiX1zw2oyO_xWhC5WxIleVJhY
        // Default Chat ID = 681929783
    }
}