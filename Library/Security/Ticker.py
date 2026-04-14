import re
from typing_extensions import Self
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import DataclassAPI

@dataclass(slots=True)
class TickerAPI(DataclassAPI):
    Raw: InitVar[str]
    Ticker: str = field(init=False, repr=True)

    def __post_init__(self, raw: str):
        self.Ticker = self._decode_(raw)

    @staticmethod
    def _decode_(value: str) -> str:
        parts = value.split()
        if len(parts) > 1:
            if parts[-1].upper() in ["CURNCY", "CURRENCY", "CURCY", "EQUITY", "INDEX", "COMDTY", "CORP", "GOVT"]:
                return parts[0].upper()
        separators = r'[/._-]'
        parts = re.split(separators, value)
        if len(parts) > 1:
            for p in parts:
                if len(p) == 6:
                    return p.upper()
            return max(parts, key=len).upper()
        return value.upper()

    def __str__(self) -> str:
        return self.Ticker

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TickerAPI):
            return self.Ticker == other.Ticker
        if isinstance(other, str):
            return self.Ticker == other.upper()
        return False