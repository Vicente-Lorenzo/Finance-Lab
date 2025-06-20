import numpy as np

class MemoryAPI:

    def __init__(self,
                 size: int,
                 input_shape: tuple,
                 action_shape: int):
        self._size = size
        self._counter = 0
        self._state_memory: np.ndarray = np.zeros((self._size, *input_shape))
        self._action_memory: np.ndarray = np.zeros((self._size, action_shape))
        self._reward_memory: np.ndarray = np.zeros(self._size)
        self._next_state_memory: np.ndarray = np.zeros((self._size, *input_shape))
        self._terminal_memory: np.ndarray = np.zeros(self._size, dtype=np.bool)

    def memorise(self, state, action, reward, next_state, done) -> None:
        index = self._counter % self._size
        self._state_memory[index] = state
        self._action_memory[index] = action
        self._reward_memory[index] = reward
        self._next_state_memory[index] = next_state
        self._terminal_memory[index] = done
        self._counter += 1

    def remember(self, batch_size) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        max_mem = min(self._counter, self._size)
        batch = np.random.choice(max_mem, batch_size)
        states = self._state_memory[batch]
        actions = self._action_memory[batch]
        rewards = self._reward_memory[batch]
        next_states = self._next_state_memory[batch]
        dones = self._terminal_memory[batch]
        return states, actions, rewards, next_states, dones
