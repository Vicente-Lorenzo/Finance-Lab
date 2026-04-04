import blpapi
from typing_extensions import Self

from Library.Service import ServiceAPI

class QueryAPI(ServiceAPI):

    _SERVICE_URI_  = "//blp/bql"
    _REQUEST_TYPE_ = "BqlRequest"

    def execute(self, query: str) -> Self:
        def _execute_():
            service = self._api_._service_(self._SERVICE_URI_)
            request = service.createRequest(self._REQUEST_TYPE_)
            request.set("query", query)
            self._api_._session_.sendRequest(request)
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            raise NotImplementedError("QueryAPI.execute: BQL response parsing is not yet implemented.")
        timer = super()._execute_(callback=_execute_)
        self._log_.info(lambda: f"Execute Operation: Executed ({timer.result()})")
        return self