
import numpy as np

from abc import ABC, abstractmethod

class Noise(ABC):
    """
    Abstract Class for Noise Processes
    """

    def __init__(self, seed=None):
        """Initialize the random number generator (shared interface for all noise types)."""
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def __call__(self):
        """Generate the next noise value based on the current internal state."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the internal state (if applicable)."""
        pass
