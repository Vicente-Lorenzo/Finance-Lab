from Library.Dataframe import pd, pl
from Library.Dataclass import DataclassAPI

class DataframeAPI:

    def __init__(self, *, legacy: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._legacy_: bool = legacy

    @staticmethod
    def flatten(data) -> list:
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        if isinstance(data, pd.Series):
            return data.to_list()
        if isinstance(data, pl.DataFrame):
            return data.to_dicts()
        if isinstance(data, pl.Series):
            return data.to_list()
        if isinstance(data, DataclassAPI):
            return [data.dict()]
        if not isinstance(data, (tuple, list, set)):
            return [data] if data else []
        if all(isinstance(item, (list, tuple, set)) for item in data):
            return list(data)
        flat = []
        for item in data:
            flat.extend(DataframeAPI.flatten(item))
        return flat

    def frame(self, data, schema: dict = None) -> pd.DataFrame | pl.DataFrame:
        data = self.flatten(data)
        df = pl.DataFrame(data=data, schema=schema, orient="row", strict=False)
        if len(df) > 0: df = df.select([s.shrink_dtype() for s in df.get_columns()])
        return df.to_pandas() if self._legacy_ else df