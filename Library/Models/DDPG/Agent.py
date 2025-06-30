import numpy as np
import torch as T
import torch.nn.functional as F

from Library.Models.Agent import AgentAPI
from Library.Models.DDPG import ActorNetworkAPI, CriticNetworkAPI
from Library.Models.Memory import MemoryAPI
from Library.Models.Noise import OrnsteinUhlenbeckNoiseAPI

class DDPGAgentAPI(AgentAPI):

    def __init__(self,
                 model: str,
                 broker: str,
                 group: str,
                 symbol: str,
                 timeframe: str,
                 alpha: float,
                 beta: float,
                 input_shape: tuple,
                 action_shape: int,
                 fc1_shape=400,
                 fc2_shape=300,
                 memory_size=1000000,
                 batch_size=64,
                 gamma=0.99,
                 tau=0.01):
        super().__init__(model=model, broker=broker, group=group, symbol=symbol, timeframe=timeframe)

        self.batch_size = batch_size
        self.gamma = gamma
        self.tau = tau

        self.memory = MemoryAPI(size=memory_size, input_shape=input_shape, action_shape=action_shape)

        self.noise = OrnsteinUhlenbeckNoiseAPI(mu=np.zeros(action_shape))

        self.actor = ActorNetworkAPI(model=model,
                                     role="actor",
                                     broker=broker,
                                     group=group,
                                     symbol=symbol,
                                     timeframe=timeframe,
                                     input_shape=input_shape,
                                     action_shape=action_shape,
                                     fc1_shape=fc1_shape,
                                     fc2_shape=fc2_shape,
                                     alpha=alpha)

        self.target_actor = ActorNetworkAPI(model=model,
                                            role="target_actor",
                                            broker=broker,
                                            group=group,
                                            symbol=symbol,
                                            timeframe=timeframe,
                                            input_shape=input_shape,
                                            action_shape=action_shape,
                                            fc1_shape=fc1_shape,
                                            fc2_shape=fc2_shape,
                                            alpha=alpha)

        self.critic = CriticNetworkAPI(model=model,
                                       role="critic",
                                       broker=broker,
                                       group=group,
                                       symbol=symbol,
                                       timeframe=timeframe,
                                       input_shape=input_shape,
                                       action_shape=action_shape,
                                       fc1_shape=fc1_shape,
                                       fc2_shape=fc2_shape,
                                       beta=beta)

        self.target_critic = CriticNetworkAPI(model=model,
                                              role="target_critic",
                                              broker=broker,
                                              group=group,
                                              symbol=symbol,
                                              timeframe=timeframe,
                                              input_shape=input_shape,
                                              action_shape=action_shape,
                                              fc1_shape=fc1_shape,
                                              fc2_shape=fc2_shape,
                                              beta=beta)

        self.update(force_tau=1)

    def save(self):
        self.actor.save()
        self.target_actor.save()
        self.critic.save()
        self.target_critic.save()
        super().save()

    def load(self):
        self.actor.load()
        self.target_actor.load()
        self.critic.load()
        self.target_critic.load()
        super().load()

    def memorise(self, state, action, reward, next_state, done) -> None:
        self.memory.memorise(state, action, reward, next_state, done)

    def remember(self, batch_size) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        return self.memory.remember(batch_size)

    def decide(self, state):
        self.actor.eval()
        state = T.tensor([state], dtype=T.float).to(self.actor.device)
        mu = self.actor.forward(state).to(self.actor.device)
        mu_prime = mu + T.tensor(self.noise(),dtype=T.float).to(self.actor.device)
        self.actor.train()
        return mu_prime.cpu().detach().numpy()[0]

    def update(self, force_tau=None):
        tau = force_tau or self.tau

        actor_params = self.actor.named_parameters()
        critic_params = self.critic.named_parameters()
        target_actor_params = self.target_actor.named_parameters()
        target_critic_params = self.target_critic.named_parameters()

        critic_state_dict = dict(critic_params)
        actor_state_dict = dict(actor_params)
        target_critic_state_dict = dict(target_critic_params)
        target_actor_state_dict = dict(target_actor_params)

        for name in critic_state_dict:
            critic_state_dict[name] = tau * critic_state_dict[name].clone() + (1 - tau) * target_critic_state_dict[name].clone()

        for name in actor_state_dict:
            actor_state_dict[name] = tau * actor_state_dict[name].clone() + (1 - tau) * target_actor_state_dict[name].clone()

        self.target_critic.load_state_dict(critic_state_dict)
        self.target_actor.load_state_dict(actor_state_dict)

    def learn(self) -> None:
        if self.memory.size < self.batch_size:
            return

        states, actions, rewards, next_states, dones = self.remember(self.batch_size)

        states = T.tensor(states, dtype=T.float).to(self.actor.device)
        actions = T.tensor(actions, dtype=T.float).to(self.actor.device)
        rewards = T.tensor(rewards, dtype=T.float).to(self.actor.device)
        next_states = T.tensor(next_states, dtype=T.float).to(self.actor.device)
        dones = T.tensor(dones).to(self.actor.device)

        target_next_actions = self.target_actor.forward(next_states)
        target_next_state_action_value = self.target_critic.forward(next_states, target_next_actions)
        state_action_value = self.critic.forward(states, actions)

        target_next_state_action_value[dones] = 0.0
        target_next_state_action_value = target_next_state_action_value.view(-1)

        target_state_action_value = rewards + self.gamma*target_next_state_action_value
        target_state_action_value = target_state_action_value.view(self.batch_size, 1)

        self.critic.optimizer.zero_grad()
        critic_loss = F.mse_loss(target_state_action_value, state_action_value)
        critic_loss.backward()
        self.critic.optimizer.step()

        self.actor.optimizer.zero_grad()
        actor_loss = -self.critic.forward(states, self.actor.forward(states))
        actor_loss = T.mean(actor_loss)
        actor_loss.backward()
        self.actor.optimizer.step()

        self.update()
