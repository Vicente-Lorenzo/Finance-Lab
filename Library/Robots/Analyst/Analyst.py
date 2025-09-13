import math
import polars as pl

from Library.Database import DatabaseAPI
from Library.Classes import Bar
from Library.Parameters import Parameters

from Library.Robots.Analyst import MarketAPI
from Library.Robots.Analyst import TechnicalAPI

class AnalystAPI:

    MARGIN = 200

    def __init__(self, analyst_management: Parameters):
        self.AnalystManagement: Parameters = analyst_management
        self.Window: int = AnalystAPI.MARGIN
        self.Market: MarketAPI = MarketAPI()

        self._technicals: list[TechnicalAPI] = []
        analyst_management = analyst_management if analyst_management else {}
        for technical_name, technical_configuration in analyst_management.items() or {}:
            technical_function, *technical_parameters = technical_configuration
            technical = TechnicalAPI(technical=technical_function, parameters=technical_parameters)
            setattr(self, technical_name, technical)
            self._technicals.append(technical)
            technical_max = max(technical_parameters) if technical_parameters else 0
            self.Window = math.ceil(max(self.Window, technical_max + AnalystAPI.MARGIN))

    def data(self) -> pl.DataFrame:
        result = pl.DataFrame()
        result = result.hstack(self.Market.data())
        for technical in self._technicals:
            result = result.hstack(technical.data())
        return result

    def head(self, n: int | None = None) -> pl.DataFrame:
        return self.data().head(n)

    def tail(self, n: int | None = None) -> pl.DataFrame:
        return self.data().tail(n)

    def init_market_data(self, data: pl.DataFrame | list[Bar]) -> None:
        data_df = DatabaseAPI.format_market_data(data)
        self.Market.init_data(data_df)
        for technical in self._technicals:
            technical.init_data(self.Market)

    def update_market_data(self, data: Bar) -> None:
        data_df = DatabaseAPI.format_market_data(data)
        self.Market.update_data(data_df)
        for technical in self._technicals:
            technical.update_data(self.Market, self.Window)

    def update_market_offset(self, offset: int) -> None:
        self.Market.update_offset(offset)
        for technical in self._technicals:
            technical.update_offset(offset)

    def __repr__(self):
        return repr(self.data())