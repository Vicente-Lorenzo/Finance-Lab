from typing import Any

import pandas as pd
import polars as pl
from Library.Utility.Dataclass import DataclassAPI
from Library.Utility.Typing import MISSING, Missing

class DataframeAPI:

    def __init__(self, *, legacy: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._legacy_: bool = legacy

    @staticmethod
    def flatten(data: Any) -> list:
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

    @staticmethod
    def parse(data: Any) -> tuple[list[str] | None, list[Any], bool]:
        if isinstance(data, pl.DataFrame):
            if data.is_empty(): return [], [], True
            return list(data.columns), data.to_dicts(), True
        if isinstance(data, pd.DataFrame):
            if data.empty: return [], [], True
            return list(data.columns), data.to_dict(orient="records"), True
        if isinstance(data, dict):
            return list(data.keys()), [data], False
        if isinstance(data, (list, tuple)):
            if not data: return [], [], True
            if isinstance(data[0], dict):
                return list(data[0].keys()), list(data), True
            if isinstance(data[0], (list, tuple)):
                return None, list(data), True
            return None, [data], False
        raise TypeError(f"Unsupported data type: {type(data)}")

    def frame(self, data: Any, schema: dict = None, legacy: bool | Missing = MISSING) -> pd.DataFrame | pl.DataFrame:
        data = self.flatten(data)
        df = pl.DataFrame(data=data, schema=schema, orient="row", strict=False)
        if len(df) > 0: df = df.select([s.shrink_dtype() for s in df.get_columns()])
        legacy = legacy if legacy is not MISSING else self._legacy_
        return df.to_pandas() if legacy else df