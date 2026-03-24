from Library.Bloomberg.Service import ServiceAPI
from Library.Dataframe import pd, pl

class HistoricalAPI(ServiceAPI):
    _SERVICE_ = "//blp/refdata"

    def fetch(self, tickers: list[str] | str, fields: list[str], start_date: str, end_date: str = None, periodicity: str = "DAILY") -> pd.DataFrame | pl.DataFrame:
        if isinstance(tickers, str): tickers = [tickers]
        def build_request(request):
            for ticker in tickers: request.getElement("securities").appendValue(ticker)
            for field in fields: request.getElement("fields").appendValue(field)
            request.set("startDate", start_date)
            if end_date: request.set("endDate", end_date)
            request.set("periodicitySelection", periodicity)
        data = self._bloomberg_.execute(self._SERVICE_, "HistoricalDataRequest", build_request)
        return self.frame(data)