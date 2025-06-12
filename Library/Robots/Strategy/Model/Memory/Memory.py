import numpy as np

class Memory:

    def __init__(self,
                 size: int,
                 input_shape: tuple,
                 action_shape: int):
        self.size = size
        self.counter = 0
        self.state_memory: np.ndarray = np.zeros((self.size, *input_shape))
        self.action_memory: np.ndarray = np.zeros((self.size, action_shape))
        self.reward_memory: np.ndarray = np.zeros(self.size)
        self.next_state_memory: np.ndarray = np.zeros((self.size, *input_shape))
        self.terminal_memory: np.ndarray = np.zeros(self.size, dtype=np.bool)

    def memorise(self, state, action, reward, next_state, done):
        index = self.counter % self.size
        self.state_memory[index] = state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.next_state_memory[index] = next_state
        self.terminal_memory[index] = done
        self.counter += 1

    def remember(self, batch_size):
        max_mem = min(self.counter, self.size)

        batch = np.random.choice(max_mem, batch_size)

        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        next_states = self.next_state_memory[batch]
        dones = self.terminal_memory[batch]

        return states, actions, rewards, next_states, dones

