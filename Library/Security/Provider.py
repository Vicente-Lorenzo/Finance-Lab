import re
from typing_extensions import Self
from dataclasses import dataclass, field, InitVar

from Library.Dataclass import DataclassAPI

@dataclass(slots=True)
class ProviderAPI(DataclassAPI):
    Raw: InitVar[str]
    Provider: str | None = field(init=False, repr=True)

    def __post_init__(self, raw: str):
        self.Provider = self._decode_(raw)

    @staticmethod
    def _decode_(value: str) -> str | None:
        parts = value.split()
        if len(parts) >= 2:
            yellows = ["CURNCY", "CURRENCY", "CURCY", "EQUITY", "INDEX", "COMDTY", "CORP", "GOVT"]
            if parts[-1].upper() in yellows:
                if len(parts) >= 3: return parts[1].upper()
                return None
        separators = r'[/._-]'
        parts = re.split(separators, value)
        if len(parts) > 1:
            ticker_candidate = max(parts, key=len)
            provider_candidate = parts[0]
            if provider_candidate.upper() != ticker_candidate.upper():
                return provider_candidate.upper()
        return None

    def __str__(self) -> str:
        return self.Provider or "Unknown"