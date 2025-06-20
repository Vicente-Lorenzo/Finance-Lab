import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from Library.Models.Network.Network import NetworkAPI

class ActorNetworkAPI(NetworkAPI):

    def __init__(self,
                 model: str,
                 role: str,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 input_shape: tuple,
                 action_shape: int,
                 fc1_shape: int,
                 fc2_shape: int,
                 alpha: float):

        self.input_shape = input_shape
        self.action_shape = action_shape
        self.fc1_shape = fc1_shape
        self.fc2_shape = fc2_shape

        self.fc1 = nn.Linear(*self.input_shape, self.fc1_shape)
        self.fc2 = nn.Linear(self.fc1_shape, self.fc2_shape)

        self.bn1 = nn.LayerNorm(self.fc1_shape)
        self.bn2 = nn.LayerNorm(self.fc2_shape)

        self.mu = nn.Linear(self.fc2_shape, self.action_shape)

        self.optimizer = optim.Adam(self.parameters(), lr=alpha)

        super().__init__(model=model, role=role, broker=broker, group=group, symbol=symbol, timeframe=timeframe)

    def init(self) -> None:
        f1 = 1. / np.sqrt(self.fc1.weight.data.size()[0])
        self.fc1.weight.data.uniform_(-f1, f1)
        self.fc1.bias.data.uniform_(-f1, f1)

        f2 = 1. / np.sqrt(self.fc2.weight.data.size()[0])
        self.fc2.weight.data.uniform_(-f2, f2)
        self.fc2.bias.data.uniform_(-f2, f2)

        f3 = 0.003
        self.mu.weight.data.uniform_(-f3, f3)
        self.mu.bias.data.uniform_(-f3, f3)

    def forward(self, state):
        action = self.fc1(state)
        action = self.bn1(action)
        action = F.relu(action)
        action = self.fc2(action)
        action = self.bn2(action)
        action = F.relu(action)
        action = T.tanh(self.mu(action))
        return action
