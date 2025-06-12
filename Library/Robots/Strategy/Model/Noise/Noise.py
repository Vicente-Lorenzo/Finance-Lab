import numpy as np

from abc import ABC, abstractmethod

class Noise(ABC):

    def __init__(self,
                 seed: int | None = None):
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def reset(self):
        pass
