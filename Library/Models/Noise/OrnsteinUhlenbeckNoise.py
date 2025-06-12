import numpy as np
from Library.Models.Noise.Noise import Noise

class OrnsteinUhlenbeckNoise(Noise):
    """
    Ornstein-Uhlenbeck Noise (Mean-Reverting Stochastic Process)

    Characteristics:
    - Distribution: Normal
    - Memory: Yes (stateful)
    - Stationary: Yes (in long run)
    - Markov: Yes
    - Bounded: No (but reverts toward mean)
    - Domain: ℝ (real numbers)

    This noise model generates temporally correlated values using an OU process,
    which tends to revert toward a long-term mean `mu` with a strength controlled
    by `theta`. The volatility of the random fluctuations is governed by `sigma`,
    and `dt` defines the timestep. Commonly used in reinforcement learning for
    exploration noise.
    """

    def __init__(self,
                 mu: np.ndarray,
                 sigma: float = 0.15,
                 theta: float = 0.2,
                 dt: float = 1e-2,
                 x0: float | None = None,
                 seed: float | None = None):
        super().__init__(seed)
        self.mu: np.ndarray = mu
        self.sigma: float = sigma
        self.theta: float = theta
        self.dt: float = dt
        self.x0: float | None = x0
        self.x_prev: float | None = None
        self.reset()

    def __call__(self):
        if np.isscalar(self.mu):
            noise = self.theta * (self.mu - self.x_prev) * self.dt \
                    + self.sigma * np.sqrt(self.dt) * self.rng.normal()
        else:
            noise = self.theta * (self.mu - self.x_prev) * self.dt \
                    + self.sigma * np.sqrt(self.dt) * self.rng.normal(size=self.mu.shape)

        self.x_prev += noise
        return self.x_prev

    def reset(self):
        if self.x0 is not None:
            self.x_prev = np.copy(self.x0)
        else:
            self.x_prev = np.zeros_like(self.mu)
