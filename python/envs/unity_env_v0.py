import gym
from gym import spaces
import numpy as np

class UnityEnv_v0(gym.Env):

    def __init__(self, render_mode=None, unity_sim_client=None, size = 1024):
        self.unity_sim_client = unity_sim_client
        self.size = size
        self.action_space = spaces.Discrete(4)
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self.is_human_controlling = False

        self._action_map = {
            0: "f".encode(),
            1: "r".encode(),
            2: "l".encode(),
            3: "h".encode(),
        }
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.unity_sim_client.send('n'.encode())
        data = self.unity_sim_client.recv(self.size)
        return data.decode(), {}

    def reward(self, obs):
        pass

    def step(self, action):
        data = None

        if self.is_human_controlling:
            data = self.unity_sim_client.recv(self.size)
        else:
            self.unity_sim_client.send(self._action_map[action])
            data = self.unity_sim_client.recv(self.size)

        terminated = False
        obs = data.decode().split(',')
        if obs[0] == '1':
            terminated = True
        
        r = self.reward(obs)

        return obs, r, terminated, False, {}

    def render(self):
        pass