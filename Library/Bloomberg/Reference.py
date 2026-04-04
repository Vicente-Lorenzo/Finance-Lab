import blpapi

from Library.Service import ServiceAPI
from Library.Dataframe import pd, pl

class ReferenceAPI(ServiceAPI):

    _SERVICE_URI_  = "//blp/refdata"
    _REQUEST_TYPE_ = "ReferenceDataRequest"

    def fetch(self, securities: str | list[str], fields: str | list[str], overrides: dict[str, str] = None) -> pd.DataFrame | pl.DataFrame:
        securities = self._api_.flatten(securities)
        fields = self._api_.flatten(fields)
        def _fetch_():
            service = self._api_._service_(self._SERVICE_URI_)
            request = service.createRequest(self._REQUEST_TYPE_)
            for sec in securities:
                request.getElement("securities").appendValue(sec)
            for fld in fields:
                request.getElement("fields").appendValue(fld)
            if overrides:
                ovr = request.getElement("overrides")
                for k, v in overrides.items():
                    o = ovr.appendElement()
                    o.setElement("fieldId", k)
                    o.setElement("value", v)
            self._api_._session_.sendRequest(request)
            data = []
            while True:
                event = self._api_._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        if not msg.hasElement("securityData"): continue
                        sec_array = msg.getElement("securityData")
                        for i in range(sec_array.numValues()):
                            sec_data = sec_array.getValueAsElement(i)
                            row = {"Security": sec_data.getElementAsString("security")}
                            if sec_data.hasElement("securityError"):
                                row["Error"] = sec_data.getElement("securityError").getElementAsString("message")
                            else:
                                fld_data = sec_data.getElement("fieldData")
                                for j in range(fld_data.numElements()):
                                    f = fld_data.getElement(j)
                                    if not f.isNull(): row[str(f.name())] = f.getValue()
                            data.append(row)
                if event.eventType() == blpapi.Event.RESPONSE: break
                if event.eventType() == blpapi.Event.TIMEOUT: continue
            return self._api_.frame(data)
        timer, df = super()._fetch_(callback=_fetch_)
        self._log_.info(lambda: f"Fetch Operation: Fetched {len(df)} reference data points ({timer.result()})")
        return df