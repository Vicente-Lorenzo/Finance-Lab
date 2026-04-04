import blpapi
from datetime import date, datetime

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl

class HistoricalAPI(ServiceAPI):

    _SERVICE_URI_  = "//blp/refdata"
    _REQUEST_TYPE_ = "HistoricalDataRequest"

    def fetch(self,
              securities: str | list[str],
              fields: str | list[str],
              start: str | date | datetime,
              stop: str | date | datetime = None,
              timeframe: str = "DAILY",
              timeout: int = 0) -> pd.DataFrame | pl.DataFrame:
        securities = self._api_.flatten(securities)
        fields = self._api_.flatten(fields)
        if isinstance(start, (date, datetime)): start = start.strftime("%Y%m%d")
        if isinstance(stop, (date, datetime)): stop = stop.strftime("%Y%m%d")
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_)
            request = service.createRequest(self._REQUEST_TYPE_)
            for sec in securities:
                request.getElement("securities").appendValue(sec)
            for fld in fields:
                request.getElement("fields").appendValue(fld)
            request.set("startDate", start)
            if stop: request.set("endDate", stop)
            request.set("periodicitySelection", str(timeframe).upper())
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(timeout)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        if not msg.hasElement("securityData"): continue
                        sec_data = msg.getElement("securityData")
                        sec_name = sec_data.getElementAsString("security")
                        fld_array = sec_data.getElement("fieldData")
                        for i in range(fld_array.numValues()):
                            fld_data = fld_array.getValueAsElement(i)
                            row = {"Security": sec_name, "Date": fld_data.getElementAsDatetime("date")}
                            for j in range(fld_data.numElements()):
                                f = fld_data.getElement(j)
                                if str(f.name()) != "date" and not f.isNull(): row[str(f.name())] = f.getValue()
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE: break
                if event.eventType() == blpapi.Event.TIMEOUT:
                    self._log_.warning(lambda: "Fetch Operation: Timeout reached while waiting for response")
                    break
            return self._api_.frame(data)
        timer, df = super()._fetch_(callback=_fetch_)
        self._log_.info(lambda: f"Fetch Operation: Fetched {len(df)} historical data points ({timer.result()})")
        return df