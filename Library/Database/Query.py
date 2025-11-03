from Library.Utility import PathAPI

class QueryAPI:

    def __init__(self, data: str | PathAPI):
        self._query = data(frame=2).read_text() if isinstance(data, PathAPI) else data

    def __call__(self, **kwargs) -> str:
        return self._query.format(**kwargs)

    def __repr__(self) -> str:
        return self._query
