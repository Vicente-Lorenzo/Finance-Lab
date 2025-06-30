import torch as T
import torch.nn as nn

from abc import ABC, abstractmethod

from Library.Logging import ConsoleAPI, TelegramAPI
from Library.Parameters import ParametersAPI

class NetworkAPI(nn.Module, ABC):

    def __init__(self,
                 model: str,
                 role: str,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str):
        super().__init__()
        self._model = model
        self._role = role
        self._broker = broker
        self._group = group
        self._symbol = symbol
        self._timeframe = timeframe

        self._filename = ParametersAPI.PATH / broker / group / symbol / timeframe / model / f"{role}"

        self._console: ConsoleAPI = ConsoleAPI(class_name=self.__class__.__name__, role_name="Network Management")
        self._telegram: TelegramAPI = TelegramAPI(class_name=self.__class__.__name__, role_name="Network Management")

        self.init()

        self.device = T.device("cuda:0" if T.cuda.is_available() else "cuda:1")
        self.to(self.device)

    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        T.save(self.state_dict(), self.checkpoint_file)
        self._console.debug(lambda: f"Saved network state for {self._model} {self._role}")

    def load(self) -> None:
        self.load_state_dict(T.load(self.checkpoint_file))
        self._console.debug(lambda: f"Loaded network state for {self._model} {self._role}")
