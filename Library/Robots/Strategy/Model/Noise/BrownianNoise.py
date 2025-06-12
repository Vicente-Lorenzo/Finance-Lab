import numpy as np
from Library.Robots.Strategy.Model.Noise.Noise import Noise

class BrownianNoise(Noise):
    """
    Brownian Motion (Wiener Process)

    Characteristics:
    - Distribution: Normal increments
    - Memory: Yes (stateful)
    - Stationary: No
    - Markov: Yes
    - Bounded: No
    - Domain: ℝ (real numbers)

    This noise model simulates Brownian motion (Wiener process), where each
    output is the cumulative sum of small Gaussian perturbations. It models
    continuous-time stochastic processes with drift `mu`, volatility `sigma`,
    and time step `dt`. The initial state is defined by `x0` (default 0).
    """

    def __init__(self,
                 mu: np.ndarray,
                 sigma: float = 0.15,
                 dt: float = 1e-2,
                 x0: float | None = None,
                 seed: int | None = None):
        super().__init__(seed)
        self.mu: np.ndarray = mu
        self.sigma: float = sigma
        self.dt: float = dt
        self.x0: float | None = x0
        self.x_prev: float | None = None
        self.reset()

    def __call__(self):
        if np.isscalar(self.mu):
            noise = self.mu * self.dt + self.sigma * np.sqrt(self.dt) * self.rng.normal()
        else:
            noise = self.mu * self.dt + self.sigma * np.sqrt(self.dt) * self.rng.normal(size=self.mu.shape)
        self.x_prev += noise
        return self.x_prev

    def reset(self):
        if self.x0 is not None:
            self.x_prev = np.copy(self.x0)
        else:
            self.x_prev = np.zeros_like(self.mu)
