import socket
import gym_envs
import gym
import numpy as np
from collections import deque
import progressbar
import random

from keras import Model, Sequential, Input
from keras.layers import Dense, Embedding, Reshape
from keras.optimizers import Adam
from keras.backend import expand_dims
from keras.models import load_model


host = 'localhost' 
port = 50000
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog)

human_controlling = False
data = None


class Agent:
    def __init__(self, enviroment, optimizer, load_models=True):
        
        # Initialize atributes
        self._state_size = enviroment.observation_space.shape[0] - 2
        self._action_size = enviroment.action_space.n
        self._optimizer = optimizer
        self.environment = enviroment
        self.episode_return = 0
        
        self.expirience_replay = deque(maxlen=2000)
        
        # Initialize discount and exploration rate
        self.gamma = 0.9
        self.epsilon = 0.25
        
        # Build networks
        if load_models:
            self.q_network = load_model('models/q_demo_learning')
            self.target_network = load_model('models/target_demo_learning')
        else:
            self.q_network = self._build_compile_model()
            self.target_network = self._build_compile_model()
        
        self.align_target_model()

    def store(self, state, action, reward, next_state, terminated):
        self.expirience_replay.append((state, int(action), reward, next_state, terminated))
    
    def _build_compile_model(self):
        model = Sequential()
        model.add(Dense(units=16, input_dim = self._state_size, activation = 'relu', name="hidden_1"))
        model.add(Dense(units=self._action_size, activation = 'linear', name="actions"))
        
        model.compile(loss='mse', optimizer=self._optimizer)

        return model

    def align_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())
    
    def act(self, state):
        if state[-1] != -1:
            return state[-1]

        if np.random.rand() <= self.epsilon:
            return self.environment.action_space.sample()
        
        q_values = self.q_network.predict(np.array([state[:-1]]), verbose=0)
        return np.argmax(q_values[0])

    def retrain(self, batch_size):
        minibatch = random.sample(self.expirience_replay, batch_size)
        q_net_preds = self.q_network.predict(np.array([state for state, _, _, _, _ in minibatch]), verbose=0, batch_size=64)
        target_net_preds = self.target_network.predict(np.array([next_state for _, _, _, next_state, _ in minibatch]), verbose=0, batch_size=64)
        
        X = []
        y = []

        for index, (state, action, reward, next_state, terminated) in enumerate(minibatch):
            qprediction = q_net_preds[index]
            targetprediction = target_net_preds[index]
            
            if terminated:
                qprediction[action] = reward
            else:
                qprediction[action] = reward + self.gamma * np.amax(targetprediction)
            
            X.append(state)
            y.append(qprediction)
        
        self.q_network.fit(np.array(X), np.array(y), epochs=1, verbose=0)

client, address = s.accept() 
environment = gym.make('UnityEnv-v0', unity_sim_client=client)
print("Client connected.")
opt = Adam(learning_rate=0.01)
agent = Agent(enviroment=environment, optimizer=opt, load_models=True)
batch_size = 64
num_of_episodes = 500
timesteps_per_episode = 1000
agent.q_network.summary()

for e in range(0, num_of_episodes):

    # Reset the enviroment
    state, _ = environment.reset()
    
    # Initialize variables
    reward = 0
    terminated = False

    bar = progressbar.ProgressBar(maxval=timesteps_per_episode/10, widgets=\
[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for timestep in range(timesteps_per_episode):
        # Run Action
        action = agent.act(state)
        
        # Take action    
        next_state, reward, terminated, _, _ = environment.step(action)
        agent.episode_return += reward

        # cut out the is terminated flag and the move-to-make flag
        state_trainable = np.array(state[1:-1])
        next_state_trainable = np.array(next_state[1:-1])
        agent.store(state_trainable, action, reward, next_state_trainable, terminated)
        
        state = next_state
        
        if terminated:
            break
            
        if len(agent.expirience_replay) > batch_size and timestep % 5 == 0:
            agent.retrain(batch_size)
        
        if timestep%10 == 0:
            bar.update(timestep/10 + 1)

    agent.align_target_model()
    agent.epsilon -= .0002

    bar.finish()
    print("**********************************")
    print("Episode: {} scored {}".format(e + 1, agent.episode_return))
    agent.episode_return = 0
    agent.q_network.save('models/q_demo_learning')
    agent.target_network.save('models/target_demo_learning')
    print("**********************************")