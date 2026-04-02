import blpapi
from typing import Callable

from Library.Service import ServiceAPI
from Library.Bloomberg.Enums import ServiceURI


class StreamingAPI(ServiceAPI):

    _SERVICE_URI_ = ServiceURI.MKTDATA

    def subscribe(self, tickers: list[str], fields: list[str], callback: Callable) -> None:
        def _subscribe():
            if not self._api_._session_.openService(self._SERVICE_URI_.value):
                raise RuntimeError(f"Failed to open service {self._SERVICE_URI_.value}")
            subscriptions = blpapi.SubscriptionList()
            for ticker in tickers:
                subscriptions.add(ticker, ",".join(fields), "", blpapi.CorrelationId(ticker))
            self._api_._session_.subscribe(subscriptions)

        timer = self._execute_(_subscribe)
        self._log_.info(lambda: f"Subscribe Operation: Subscribed to {len(tickers)} tickers ({timer.result()})")