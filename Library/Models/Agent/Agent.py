from abc import ABC, abstractmethod

import numpy as np

from Library.Logging.Console import ConsoleAPI
from Library.Logging.Telegram import TelegramAPI

class AgentAPI(ABC):

    def __init__(self,
                 model: str,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str):
        super().__init__()
        self._model = model
        self._broker = broker
        self._group = group
        self._symbol = symbol
        self._timeframe = timeframe

        self._console: ConsoleAPI = ConsoleAPI(class_name=self.__class__.__name__, role_name="Agent Management")
        self._telegram: TelegramAPI = TelegramAPI(class_name=self.__class__.__name__, role_name="Agent Management")

    @abstractmethod
    def save(self) -> None:
        self._console.debug(lambda: f"Saved agent state for {self._model}")

    @abstractmethod
    def load(self) -> None:
        self._console.debug(lambda: f"Loaded agent state for {self._model}")

    @abstractmethod
    def memorise(self, state, action, reward, next_state, done) -> None:
        raise NotImplementedError

    @abstractmethod
    def remember(self, batch_size) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        raise NotImplementedError

    @abstractmethod
    def decide(self, state) -> np.ndarray | float | int:
        raise NotImplementedError

    @abstractmethod
    def update(self, *args) -> None:
        raise NotImplementedError

    @abstractmethod
    def learn(self) -> None:
        raise NotImplementedError
