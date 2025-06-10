import numpy as np
from Library.Robots.Strategy.AI.Noise.Noise import Noise

class GaussianNoise(Noise):
    """
    Gaussian White Noise

    Characteristics:
    - Distribution: Normal
    - Memory: No
    - Stationary: Yes
    - Markov: Yes
    - Bounded: No
    - Domain: ℝ (real numbers)

    This noise model generates i.i.d. samples from a normal distribution
    with mean `mu` and standard deviation `sigma`. It is typically used
    to simulate purely random (white) noise in continuous domains.
    """

    def __init__(self, mu, sigma=0.15, seed=None):
        super().__init__(seed)
        self.mu = mu
        self.sigma = sigma

    def __call__(self):
        if np.isscalar(self.mu):
            return self.mu + self.sigma * self.rng.normal()
        else:
            return self.mu + self.sigma * self.rng.normal(size=self.mu.shape)

    def reset(self):
        pass
