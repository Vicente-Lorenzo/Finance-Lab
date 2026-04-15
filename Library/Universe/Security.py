from typing_extensions import Self
from dataclasses import dataclass, field, InitVar

from Library.Utility.Dataclass import DataclassAPI
from Library.Universe.Ticker import TickerAPI
from Library.Universe.Provider import ProviderAPI
from Library.Universe.Category import CategoryAPI

@dataclass(slots=True)
class SecurityAPI(DataclassAPI):
    Raw: InitVar[str | Self]
    Ticker: TickerAPI = field(init=False, repr=True)
    Provider: ProviderAPI = field(init=False, repr=True)
    Category: CategoryAPI = field(init=False, repr=True)

    def __post_init__(self, raw: str | Self):
        if isinstance(raw, SecurityAPI):
            self.Ticker = raw.Ticker
            self.Provider = raw.Provider
            self.Category = raw.Category
        else:
            self.Ticker = TickerAPI(raw)
            self.Provider = ProviderAPI(raw)
            self.Category = CategoryAPI(raw)

    @property
    def Bloomberg(self) -> str:
        t = str(self.Ticker)
        p = self.Provider.Provider if self.Provider.Provider else ""
        c = self.Category.Bloomberg
        return f"{t} {p} {c}".strip().replace("  ", " ")

    def __str__(self) -> str:
        return f"{self.Ticker} ({self.Category})"

    def __repr__(self) -> str:
        return f"SecurityAPI(Ticker='{self.Ticker}', Provider='{self.Provider}', Category='{self.Category}')"
