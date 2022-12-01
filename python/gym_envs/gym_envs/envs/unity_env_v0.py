import gym
from gym import spaces
import numpy as np

class UnityEnv_v0(gym.Env):

    def __init__(self, render_mode=None, unity_sim_client=None, size = 1024, reward_granularity=100):
        self.unity_sim_client = unity_sim_client
        self.size = size
        self.observation_space = spaces.Box(0, 100, shape=(6,))
        self.action_space = spaces.Discrete(3)
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self.reward_granularity = reward_granularity
        self.world_units_per_grid = 100 / reward_granularity 
        self.reward_grid = np.zeros(shape=(reward_granularity, reward_granularity))

        self.is_human_controlling = False

        self._action_map = {
            0: "f".encode(),
            1: "r".encode(),
            2: "l".encode(),
        }
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.unity_sim_client.send('n'.encode())
        data = self.unity_sim_client.recv(self.size)
        self.reward_grid = np.zeros(shape=(self.reward_granularity, self.reward_granularity))
        return self._getobs(data), {}

    def _getobs(self, data):
        return np.array(data.decode().split(',')).astype(np.float32)

    def reward(self, obs):
        if obs[0] == 1:
            return 1000
        
        x = obs[1]
        y = obs[2]

        distance_to_tennisball = .01 * (np.abs(obs[1]-obs[4]) + np.abs(obs[2]-obs[5]))
        same_spot_penality = self.reward_grid[int(x//self.world_units_per_grid)][int(y//self.world_units_per_grid)]
        
        # reward places we have not been yet
        return -distance_to_tennisball + same_spot_penality

    def step(self, action):
        data = None

        if self.is_human_controlling:
            data = self.unity_sim_client.recv(self.size)
        else:
            self.unity_sim_client.send(self._action_map[action])
            data = self.unity_sim_client.recv(self.size)

        terminated = False
        obs = self._getobs(data)
        if obs[0] == 1:
            terminated = True
        
        r = self.reward(obs)

        x = obs[1]
        y = obs[2]

        self.reward_grid[int(x//self.world_units_per_grid)][int(y//self.world_units_per_grid)] -= .01

        return obs, r, terminated, False, {}

    def render(self):
        pass