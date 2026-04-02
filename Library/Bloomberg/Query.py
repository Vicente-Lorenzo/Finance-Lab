import blpapi

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl
from Library.Bloomberg.Enums import ServiceURI, RequestType


class QueryAPI(ServiceAPI):

    _SERVICE_URI_ = ServiceURI.BQL

    def execute(self, query: str) -> pd.DataFrame | pl.DataFrame:
        def _do():
            service = self._api_._service_(self._SERVICE_URI_.value)
            request = service.createRequest(RequestType.BQL_DATA.value)
            request.set("query", query)
            self._api_._session_.sendRequest(request)
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            raise NotImplementedError("QueryAPI.execute: BQL response parsing is not yet implemented.")

        timer = self._execute_(_do)
        self._log_.info(lambda: f"Execute Operation: Executed ({timer.result()})")
        return self