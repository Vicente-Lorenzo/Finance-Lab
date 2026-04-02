import blpapi
from datetime import date, datetime

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl
from Library.Bloomberg.Enums import ServiceURI, RequestType, Periodicity


class HistoricalAPI(ServiceAPI):

    _SERVICE_URI_ = ServiceURI.REFDATA

    def fetch(self,
              securities: str | list[str],
              fields: str | list[str],
              start_date: str | date | datetime,
              end_date: str | date | datetime = None,
              periodicity: Periodicity | str = Periodicity.DAILY) -> pd.DataFrame | pl.DataFrame:
        securities = self._api_.flatten(securities)
        fields = self._api_.flatten(fields)
        if isinstance(start_date, (date, datetime)): start_date = start_date.strftime("%Y%m%d")
        if isinstance(end_date, (date, datetime)): end_date = end_date.strftime("%Y%m%d")
        if isinstance(periodicity, Periodicity): periodicity = periodicity.value
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_.value)
            request = service.createRequest(RequestType.HISTORICAL_DATA.value)
            for sec in securities:
                request.getElement("securities").appendValue(sec)
            for fld in fields:
                request.getElement("fields").appendValue(fld)
            request.set("startDate", start_date)
            if end_date: request.set("endDate", end_date)
            request.set("periodicitySelection", periodicity)
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        security_data = msg.getElement("securityData")
                        security_name = security_data.getElementAsString("security")
                        field_data_array = security_data.getElement("fieldData")
                        for i in range(field_data_array.numValues()):
                            field_data = field_data_array.getValueAsElement(i)
                            row = {"security": security_name, "date": field_data.getElementAsDatetime("date")}
                            for j in range(field_data.numElements()):
                                field = field_data.getElement(j)
                                if str(field.name()) != "date":
                                    row[str(field.name())] = field.getValue()
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            return self._api_.frame(data)
        timer, df = self._fetch_(_fetch_)
        self._log_.info(lambda: f"Fetch Operation: Fetched {len(df)} historical data points ({timer.result()})")
        return df