import gym
from gym import spaces
import numpy as np

class UnityEnv_v0(gym.Env):

    def __init__(self, render_mode=None, unity_sim_client=None, size = 1024):
        self.unity_sim_client = unity_sim_client
        self.size = size
        self.observation_space = spaces.Box(0, 100, shape=(7,))
        self.action_space = spaces.Discrete(3)
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self._action_map = {
            0: "f".encode(),
            1: "r".encode(),
            2: "l".encode(),
        }
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.unity_sim_client.send('n'.encode())
        data = self.unity_sim_client.recv(self.size)
        return self._getobs(data), {}

    def _getobs(self, data):
        return np.array(data.decode().split(',')).astype(np.float32)


    def reward(self, obs):
        if obs[0] == 1:
            return 100
        
        return -1

    # action -1 means wait for a human move
    def step(self, action):
        data = None

        if action == -1:
            data = self.unity_sim_client.recv(self.size)
        else:
            self.unity_sim_client.send(self._action_map[action])
            data = self.unity_sim_client.recv(self.size)

        terminated = False
        obs = self._getobs(data)
        if obs[0] == 1:
            terminated = True
        
        r = self.reward(obs)
        return obs, r, terminated, False, {}

    def render(self):
        pass