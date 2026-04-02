import blpapi
from datetime import datetime

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl
from Library.Bloomberg.Enums import ServiceURI, RequestType, EventType


class IntradayAPI(ServiceAPI):

    _SERVICE_URI_ = ServiceURI.REFDATA

    def fetch_bars(self,
                   ticker: str,
                   start_datetime: datetime,
                   end_datetime: datetime = None,
                   interval: int = 1,
                   event_type: EventType | str = EventType.TRADE) -> pd.DataFrame | pl.DataFrame:
        if isinstance(event_type, EventType): event_type = event_type.value

        def _request():
            service = self._api_._service_(self._SERVICE_URI_.value)
            request = service.createRequest(RequestType.INTRADAY_BAR.value)
            request.set("security", ticker)
            request.set("eventType", event_type)
            request.set("interval", interval)
            request.set("startDateTime", start_datetime.strftime("%Y-%m-%dT%H:%M:%S"))
            if end_datetime: request.set("endDateTime", end_datetime.strftime("%Y-%m-%dT%H:%M:%S"))
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        bar_data = msg.getElement("barData").getElement("barTickData")
                        for i in range(bar_data.numValues()):
                            bar = bar_data.getValueAsElement(i)
                            row = {str(field.name()): field.getValue() for field in bar.elements()}
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            return self._api_.frame(data)

        timer, df = self._fetch_(_request)
        self._log_.info(lambda: f"Fetch Bars Operation: Fetched {len(df)} data points ({timer.result()})")
        return df

    def fetch_ticks(self,
                    ticker: str,
                    start_datetime: datetime,
                    end_datetime: datetime = None,
                    event_types: list[EventType | str] = None) -> pd.DataFrame | pl.DataFrame:
        if event_types is None: event_types = [EventType.TRADE]
        event_types = [e.value if isinstance(e, EventType) else e for e in event_types]

        def _request():
            service = self._api_._service_(self._SERVICE_URI_.value)
            request = service.createRequest(RequestType.INTRADAY_TICK.value)
            request.set("security", ticker)
            request.set("startDateTime", start_datetime.strftime("%Y-%m-%dT%H:%M:%S"))
            if end_datetime: request.set("endDateTime", end_datetime.strftime("%Y-%m-%dT%H:%M:%S"))
            event_types_element = request.getElement("eventTypes")
            for event_type in event_types: event_types_element.appendValue(event_type)
            request.set("includeConditionCodes", True)
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        tick_data = msg.getElement("tickData").getElement("tickData")
                        for i in range(tick_data.numValues()):
                            tick = tick_data.getValueAsElement(i)
                            row = {str(field.name()): field.getValue() for field in tick.elements()}
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            return self._api_.frame(data)

        timer, df = self._fetch_(_request)
        self._log_.info(lambda: f"Fetch Ticks Operation: Fetched {len(df)} data points ({timer.result()})")
        return df