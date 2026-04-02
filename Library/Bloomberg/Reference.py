import blpapi

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl
from Library.Bloomberg.Enums import ServiceURI, RequestType

class ReferenceAPI(ServiceAPI):

    _SERVICE_URI_ = ServiceURI.REFDATA

    def fetch(self,
              securities: str | list[str],
              fields: str | list[str],
              overrides: dict[str, str] = None) -> pd.DataFrame | pl.DataFrame:
        securities = self._api_.flatten(securities)
        fields = self._api_.flatten(fields)
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_.value)
            request = service.createRequest(RequestType.REFERENCE_DATA.value)
            for sec in securities:
                request.getElement("securities").appendValue(sec)
            for fld in fields:
                request.getElement("fields").appendValue(fld)
            if overrides:
                overrides_element = request.getElement("overrides")
                for key, value in overrides.items():
                    override = overrides_element.appendElement()
                    override.setElement("fieldId", key)
                    override.setElement("value", value)
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        security_data_array = msg.getElement("securityData")
                        for i in range(security_data_array.numValues()):
                            security_data = security_data_array.getValueAsElement(i)
                            row = {"security": security_data.getElementAsString("security")}
                            if security_data.hasElement("securityError"):
                                row["error"] = security_data.getElement("securityError").getElementAsString("message")
                            else:
                                field_data = security_data.getElement("fieldData")
                                for j in range(field_data.numElements()):
                                    field = field_data.getElement(j)
                                    row[str(field.name())] = field.getValue()
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            return self._api_.frame(data)
        timer, df = self._fetch_(_fetch_)
        self._log_.info(lambda: f"Fetch Operation: Fetched {len(df)} reference data points ({timer.result()})")
        return df