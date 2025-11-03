from Library.Utility import PathAPI

class QueryAPI:

    def __init__(self, data: str | PathAPI):
        self._query: str = data(frame=2).read_text() if isinstance(data, PathAPI) else data

    def __call__(self, **kwargs) -> str:
        return self._query.format(**kwargs)
