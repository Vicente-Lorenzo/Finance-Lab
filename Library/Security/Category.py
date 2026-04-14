from typing_extensions import Self
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import DataclassAPI

@dataclass(slots=True)
class CategoryAPI(DataclassAPI):
    Raw: InitVar[str]
    Primary: str = field(init=False, repr=True)
    Secondary: str | None = field(init=False, repr=True)

    def __post_init__(self, raw: str):
        self.Primary, self.Secondary = self._decode_(raw)

    @staticmethod
    def _decode_(value: str) -> tuple[str, str | None]:
        v = value.upper()
        if any(h in v for h in ["CURNCY", "CURRENCY", "CURCY"]):
            p, s = "Forex", None
            if any(m in v for m in ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]): s = "Majors"
            return p, s
        if "EQUITY" in v: return "Equities", None
        if "INDEX" in v: return "Indices", None
        if "COMDTY" in v: return "Commodities", None
        if "CORP" in v or "GOVT" in v: return "Bonds", None
        clean = v.replace("/", "").replace(".", "").replace("-", "").replace("_", "")
        if len(clean) > 6:
            curs = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD"]
            for i in range(len(clean) - 5):
                sub = clean[i:i+6]
                if any(c in sub for c in curs):
                    p, s = "Forex", None
                    if any(m in sub for m in ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]): s = "Majors"
                    return p, s
        if len(clean) == 6:
            curs = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD"]
            if any(c in clean for c in curs):
                p, s = "Forex", None
                if any(m in clean for m in ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]): s = "Majors"
                return p, s
        if any(m in clean for m in ["XAU", "XAG", "XPT", "XPD", "GOLD", "SILVER"]):
            return "Metals", "Spot"
        return "Other", None

    @property
    def Bloomberg(self) -> str:
        m = {"Forex": "Curncy", "Equities": "Equity", "Indices": "Index", "Commodities": "Comdty", "Bonds": "Corp", "Metals": "Curncy"}
        return m.get(self.Primary, "Curncy")

    def __str__(self) -> str:
        if self.Secondary: return f"{self.Primary} ({self.Secondary})"
        return self.Primary