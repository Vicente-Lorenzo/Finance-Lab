import blpapi
from enum import Enum
from datetime import datetime

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl

class EventType(str, Enum):
    TRADE    = "TRADE"
    BID      = "BID"
    ASK      = "ASK"
    BID_BEST = "BID_BEST"
    ASK_BEST = "ASK_BEST"
    AT_TRADE = "AT_TRADE"
    AT_BID   = "AT_BID"
    AT_ASK   = "AT_ASK"

class IntradayAPI(ServiceAPI):

    _SERVICE_URI_       = "//blp/refdata"
    _BAR_REQUEST_TYPE_  = "IntradayBarRequest"
    _TICK_REQUEST_TYPE_ = "IntradayTickRequest"

    def bars(self, security: str, start: datetime, stop: datetime = None, interval: int = 1, event_type: str | EventType = EventType.TRADE) -> pd.DataFrame | pl.DataFrame:
        if isinstance(event_type, EventType): event_type = event_type.value
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_)
            request = service.createRequest(self._BAR_REQUEST_TYPE_)
            request.set("security", security)
            request.set("eventType", event_type)
            request.set("interval", interval)
            request.set("startDateTime", start.strftime("%Y-%m-%dT%H:%M:%S"))
            if stop: request.set("endDateTime", stop.strftime("%Y-%m-%dT%H:%M:%S"))
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        if not msg.hasElement("barData"): continue
                        bar_data = msg.getElement("barData").getElement("barTickData")
                        for i in range(bar_data.numValues()):
                            bar = bar_data.getValueAsElement(i)
                            row = {str(f.name()): f.getValue() for f in bar.elements() if not f.isNull()}
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE: break
                if event.eventType() == blpapi.Event.TIMEOUT: continue
            return self._api_.frame(data)
        timer, df = super()._fetch_(callback=_fetch_)
        self._log_.info(lambda: f"Bars Operation: Fetched {len(df)} bars ({timer.result()})")
        return df

    def ticks(self, security: str, start: datetime, stop: datetime = None, event_types: list[str | EventType] = None) -> pd.DataFrame | pl.DataFrame:
        if event_types is None: event_types = [EventType.TRADE]
        event_types = [e.value if isinstance(e, EventType) else e for e in event_types]
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_)
            request = service.createRequest(self._TICK_REQUEST_TYPE_)
            request.set("security", security)
            request.set("startDateTime", start.strftime("%Y-%m-%dT%H:%M:%S"))
            if stop: request.set("endDateTime", stop.strftime("%Y-%m-%dT%H:%M:%S"))
            ev_types = request.getElement("eventTypes")
            for et in event_types: ev_types.appendValue(et)
            request.set("includeConditionCodes", True)
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        if not msg.hasElement("tickData"): continue
                        tick_data = msg.getElement("tickData").getElement("tickData")
                        for i in range(tick_data.numValues()):
                            tick = tick_data.getValueAsElement(i)
                            row = {str(f.name()): f.getValue() for f in tick.elements() if not f.isNull()}
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE: break
                if event.eventType() == blpapi.Event.TIMEOUT: continue
            return self._api_.frame(data)
        timer, df = super()._fetch_(callback=_fetch_)
        self._log_.info(lambda: f"Ticks Operation: Fetched {len(df)} ticks ({timer.result()})")
        return df