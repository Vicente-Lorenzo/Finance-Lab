from abc import ABC
from typing import TYPE_CHECKING
from Library.Logging import HandlerLoggingAPI
from Library.Dataframe import pd, pl

if TYPE_CHECKING:
    from Library.Bloomberg.Bloomberg import BloombergAPI

class ServiceAPI(ABC):
    _SERVICE_: str = None

    def __init__(self, bloomberg: 'BloombergAPI') -> None:
        self._bloomberg_ = bloomberg
        self._log_ = HandlerLoggingAPI(self.__class__.__name__)

    def frame(self, data: list, schema: dict = None) -> pd.DataFrame | pl.DataFrame:
        return self._bloomberg_.frame(data, schema)