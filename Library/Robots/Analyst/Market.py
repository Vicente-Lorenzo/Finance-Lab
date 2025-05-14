import polars as pl

from Agents.Analyst.Series import SeriesAPI

class MarketAPI:

    def __init__(self):
        self._offset: int = 1
        self._series: list[SeriesAPI] | None = None
        self._data: pl.DataFrame | None = None

    def data(self) -> pl.DataFrame:
        return self._data
    
    def head(self, n: int | None = None) -> pl.DataFrame:
        return self._data.head(n)

    def tail(self, n: int | None = None) -> pl.DataFrame:
        return self._data.tail(n)

    def last(self, shift: int = 0) -> pl.DataFrame:
        return self.data()[-(self._offset + shift)]
    
    def init_data(self, data: pl.DataFrame) -> None:
        self._series = []
        self._data = pl.DataFrame()
        for series in data.iter_columns():
            tseries = SeriesAPI(series.name)
            setattr(self, series.name, tseries)
            self._series.append(tseries)
            self._data = self._data.with_columns(series)
        self._data = self._data.rechunk()
        for tseries in self._series:
            tseries.init_data(self._data)
            
    def update_data(self, data: pl.DataFrame) -> None:
        self._data.extend(data)
        
    def update_offset(self, offset: int) -> None:
        self._offset = offset
        for tseries in self._series:
            tseries.update_offset(offset)

    def __repr__(self):
        return repr(self.data())
