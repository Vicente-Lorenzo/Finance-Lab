from dataclasses import dataclass, field

from Library.Dataclass import DataclassAPI

@dataclass(slots=True, kw_only=True)
class TelegramConfigurationAPI(DataclassAPI):
    Token: str = field(init=True, repr=True)
    ChatID: str = field(init=True, repr=True)
