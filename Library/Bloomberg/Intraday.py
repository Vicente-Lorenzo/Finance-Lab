from Library.Bloomberg.Service import ServiceAPI
from Library.Dataframe import pd, pl

class IntradayAPI(ServiceAPI):
    _SERVICE_ = "//blp/refdata"

    def bars(self, ticker: str, start_datetime: str, end_datetime: str = None, interval: int = 1, event_type: str = "TRADE") -> pd.DataFrame | pl.DataFrame:
        def build_request(request):
            request.set("security", ticker)
            request.set("eventType", event_type)
            request.set("interval", interval)
            request.set("startDateTime", start_datetime)
            if end_datetime: request.set("endDateTime", end_datetime)
        data = self._bloomberg_.execute(self._SERVICE_, "IntradayBarRequest", build_request)
        return self.frame(data)

    def ticks(self, ticker: str, start_datetime: str, end_datetime: str = None, event_types: list[str] = None) -> pd.DataFrame | pl.DataFrame:
        if event_types is None: event_types = ["TRADE"]
        def build_request(request):
            request.set("security", ticker)
            request.set("startDateTime", start_datetime)
            if end_datetime: request.set("endDateTime", end_datetime)
            event_types_element = request.getElement("eventTypes")
            for event_type in event_types: event_types_element.appendValue(event_type)
            request.set("includeConditionCodes", True)
        data = self._bloomberg_.execute(self._SERVICE_, "IntradayTickRequest", build_request)
        return self.frame(data)