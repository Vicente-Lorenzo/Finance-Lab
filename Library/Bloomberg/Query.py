from Library.Bloomberg.Service import ServiceAPI
from Library.Dataframe import pd, pl

class QueryAPI(ServiceAPI):
    _SERVICE_ = "//blp/bql"

    def execute(self, query: str) -> pd.DataFrame | pl.DataFrame:
        def build_request(request): request.set("query", query)
        data = self._bloomberg_.execute(self._SERVICE_, "BqlRequest", build_request)
        return self.frame(data)