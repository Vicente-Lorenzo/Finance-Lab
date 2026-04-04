import blpapi
from typing import Callable

from Library.Service import ServiceAPI

class StreamingAPI(ServiceAPI):

    _SERVICE_URI_ = "//blp/mktdata"

    def subscribe(self, securities: str | list[str], fields: list[str], callback: Callable, frame: bool = True) -> None:
        securities = self._api_.flatten(securities)
        def _execute_():
            if not self._api_._session_.openService(self._SERVICE_URI_):
                raise RuntimeError(f"Failed to open service {self._SERVICE_URI_}")
            subs = blpapi.SubscriptionList()
            for s in securities:
                subs.add(s, ",".join(fields), "", blpapi.CorrelationId(s))
            self._api_._session_.subscribe(subs)
            while True:
                ev = self._api_._session_.nextEvent(100)
                if ev.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                    for msg in ev:
                        row = {"Security": str(msg.correlationId().value())}
                        for i in range(msg.numElements()):
                            f = msg.getElement(i)
                            if not f.isNull(): row[str(f.name())] = f.getValue()
                        callback(self._api_.frame([row]) if frame else row)
                elif ev.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    pass
                elif ev.eventType() == blpapi.Event.TIMEOUT:
                    continue
        timer = super()._execute_(callback=_execute_)
        self._log_.info(lambda: f"Subscribe Operation: Subscribed to {len(securities)} securities ({timer.result()})")