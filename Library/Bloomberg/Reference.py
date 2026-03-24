from Library.Bloomberg.Service import ServiceAPI
from Library.Dataframe import pd, pl

class ReferenceAPI(ServiceAPI):
    _SERVICE_ = "//blp/refdata"

    def fetch(self, tickers: list[str] | str, fields: list[str] | str, overrides: dict = None) -> pd.DataFrame | pl.DataFrame:
        if isinstance(tickers, str): tickers = [tickers]
        if isinstance(fields, str): fields = [fields]
        def build_request(request):
            for ticker in tickers: request.getElement("securities").appendValue(ticker)
            for field in fields: request.getElement("fields").appendValue(field)
            if overrides:
                overrides_element = request.getElement("overrides")
                for key, value in overrides.items():
                    override = overrides_element.appendElement()
                    override.setElement("fieldId", key)
                    override.setElement("value", value)
        data = self._bloomberg_.execute(self._SERVICE_, "ReferenceDataRequest", build_request)
        return self.frame(data)