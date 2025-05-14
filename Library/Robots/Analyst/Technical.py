import polars as pl

from Agents.Container.Classes import Technical
from Agents.Analyst.Market import MarketAPI
from Agents.Analyst.Series import SeriesAPI
from Agents.Analyst.Technicals import Technicals

class TechnicalAPI:

    def __init__(self, technical: str, parameters: list | None = None):
        self._offset: int = 1

        self._technical: Technical = getattr(Technicals, technical)
        self._parameters: dict = dict(zip(self._technical.Parameters.keys(), parameters))
        self._sids = [f"{technical}_{'_'.join(map(str, parameters)) + '_' if parameters else ''}{output}" for output in self._technical.Output]

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

    def calculate(self, market: MarketAPI, window: int | None = None) -> pl.DataFrame:
        input_series = [tseries.tail(window) if window else tseries.data() for tseries in self._technical.Input(market)]
        df = pl.DataFrame(self._technical.Function(input_series, **self._parameters))
        df.columns = self._sids
        return df

    def init_data(self, market: MarketAPI) -> None:
        self._series = []
        self._data = pl.DataFrame()
        output_df = self.calculate(market)
        for name, sid, series in zip(self._technical.Output, self._sids, output_df):
            series = series.fill_nan(None)
            tseries = SeriesAPI(sid)
            setattr(self, name, tseries)
            self._series.append(tseries)
            self._data = self._data.with_columns(series)
        self._data = self._data.rechunk()
        for tseries in self._series:
            tseries.init_data(self._data)

    def update_data(self, market: MarketAPI, window: int) -> None:
        self._data.extend(self.calculate(market, window)[-1])

    def update_offset(self, offset: int) -> None:
        self._offset = offset
        for tseries in self._series:
            tseries.update_offset(offset)

    def filter_buy(self, market: MarketAPI | None = None, shift: int = 0) -> bool:
        return self._technical.FilterBuy(market, self, shift)

    def filter_sell(self, market: MarketAPI | None = None, shift: int = 0) -> bool:
        return self._technical.FilterSell(market, self, shift)

    def signal_buy(self, market: MarketAPI | None = None, shift: int = 0) -> bool:
        return self._technical.SignalBuy(market, self, shift)

    def signal_sell(self, market: MarketAPI | None = None, shift: int = 0) -> bool:
        return self._technical.SignalSell(market, self, shift)

    def __repr__(self):
        return repr(self.data())
