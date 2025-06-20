import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from Library.Models.Network.Network import NetworkAPI

class CriticAPI(NetworkAPI):

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
                 beta: float):

        self.input_shape = input_shape
        self.action_shape = action_shape
        self.fc1_shape = fc1_shape
        self.fc2_shape = fc2_shape

        self.fc1 = nn.Linear(*self.input_shape, self.fc1_shape)
        self.fc2 = nn.Linear(self.fc1_shape, self.fc2_shape)

        self.bn1 = nn.LayerNorm(self.fc1_shape)
        self.bn2 = nn.LayerNorm(self.fc2_shape)

        self.action_value = nn.Linear(self.action_shape, self.fc2_shape)
        self.q = nn.Linear(self.fc2_shape, 1)

        self.optimizer = optim.Adam(self.parameters(), lr=beta, weight_decay=0.01)

        super().__init__(model=model, role=role, broker=broker, group=group, symbol=symbol, timeframe=timeframe)

    def init(self):
        f1 = 1. / np.sqrt(self.fc1.weight.data.size()[0])
        self.fc1.weight.data.uniform_(-f1, f1)
        self.fc1.bias.data.uniform_(-f1, f1)

        f2 = 1. / np.sqrt(self.fc2.weight.data.size()[0])
        self.fc2.weight.data.uniform_(-f2, f2)
        self.fc2.bias.data.uniform_(-f2, f2)

        f3 = 0.003
        self.q.weight.data.uniform_(-f3, f3)
        self.q.bias.data.uniform_(-f3, f3)

        f4 = 1. / np.sqrt(self.action_value.weight.data.size()[0])
        self.action_value.weight.data.uniform_(-f4, f4)
        self.action_value.bias.data.uniform_(-f4, f4)

    def forward(self, state, action):
        state_value = self.fc1(state)
        state_value = self.bn1(state_value)
        state_value = F.relu(state_value)
        state_value = self.fc2(state_value)
        state_value = self.bn2(state_value)

        action_value = self.action_value(action)
        state_action_value = F.relu(T.add(state_value, action_value))
        state_action_value = self.q(state_action_value)

        return state_action_value