from Library.Bloomberg.Service import ServiceAPI

class StreamingAPI(ServiceAPI):
    _SERVICE_ = "//blp/mktdata"

    def subscribe(self, tickers: list[str], fields: list[str], callback):
        import blpapi
        self._bloomberg_.connect()
        if not self._bloomberg_._session_.openService(self._SERVICE_): raise RuntimeError(f"Failed to open service {self._SERVICE_}")
        subscriptions = blpapi.SubscriptionList()
        for ticker in tickers: subscriptions.add(ticker, ",".join(fields), "", blpapi.CorrelationId(ticker))
        self._bloomberg_._session_.subscribe(subscriptions)
        self._log_.info(lambda: f"Streaming Request: Subscribed to {len(tickers)} tickers")