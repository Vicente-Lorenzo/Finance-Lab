import numpy as np
from Library.Robots.Strategy.Model.Noise.Noise import Noise

class GeometricBrownianNoise(Noise):
    """
    Geometric Brownian Motion (Log-Normal Process)

    Characteristics:
    - Distribution: Log-normal
    - Memory: Yes (stateful)
    - Stationary: No
    - Markov: Yes
    - Bounded: No (but always positive)
    - Domain: ℝ⁺ (positive real numbers)

    This noise model simulates a stochastic process where each value is a
    multiplicative update based on Brownian motion. It is often used to model
    stock prices, where the returns are normally distributed but the process
    itself is log-normally distributed. Initial value is `s0` (default 1).
    """

    def __init__(self, mu, sigma=0.15, dt=1e-2, s0=None, seed=None):
        super().__init__(seed)
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.s0 = s0
        self.s_prev = None
        self.reset()

    def __call__(self):
        if np.isscalar(self.mu):
            noise = self.rng.normal()
            drift = (self.mu - 0.5 * self.sigma ** 2) * self.dt
            diffusion = self.sigma * np.sqrt(self.dt) * noise
        else:
            noise = self.rng.normal(size=self.mu.shape)
            drift = (self.mu - 0.5 * self.sigma ** 2) * self.dt
            diffusion = self.sigma * np.sqrt(self.dt) * noise

        self.s_prev *= np.exp(drift + diffusion)
        return self.s_prev

    def reset(self):
        if self.s0 is not None:
            self.s_prev = np.copy(self.s0)
        else:
            self.s_prev = np.ones_like(self.mu)
