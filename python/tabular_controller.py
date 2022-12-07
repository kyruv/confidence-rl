import gym
import gym_envs
import numpy as np
import matplotlib.pyplot as plt
import socket
from datetime import datetime

# row, column, rotation, action
# if you need to define for the first time use this
# q_table = np.zeros([5,12,8,3])
q_table = np.load("models/qtable.npy")

# if you need to define for the first time use this
# q_visit_count = np.zeros([5,12,8,3])
q_visit_count = np.load("models/qvisitcount.npy")

# hyperparams
alpha = .01
num_episodes = 10000
gamma = .9

# make it deterministic
np.random.seed(1)

def get_greedy_action(state, epsilon):
    if np.random.uniform(0,1) < epsilon:
        return np.random.randint(0, 3)
    
    best_action, _ = get_best_action_from(state)
    
    return best_action

def get_agent_space(observation):
    return (int(observation[1]), int(observation[2]), int(observation[3]//45))

def get_best_action_from(state):
    best_action = None
    best_score = None
    for action in range(3):
        action_score = q_table[state[0]][state[1]][state[2]][action]
        if best_score == None or action_score > best_score:
            best_score = action_score
            best_action = action
    return best_action, best_score

def print_policy():
    policy_print = [[[""] * 8 for c in range(12)] for r in range(5)]
    for row in range(5):
        for col in range(12):
            for rot in range(8):
                best_action, _ = get_best_action_from((row,col,rot))
                repr = "-"
                if best_action == 0:
                    repr = "f"
                elif best_action == 1:
                    repr = "r"
                else:
                    repr = "l"
                policy_print[row][col][rot] = repr
            
    print(policy_print)
    
def print_best_q_grid():
    best_q_grid = [[[""] * 8 for c in range(12)] for r in range(5)]
    for row in range(5):
        for col in range(12):
            for rot in range(8):
                _, best_score = get_best_action_from((row,col,rot))
                best_q_grid[row][col][rot] = "{:.5f}".format(best_score)
                 
    print(best_q_grid)

def get_confidence_in_state(agent_loc):
    return sum(q_visit_count[agent_loc[0]][agent_loc[1]][agent_loc[2]])

cell_to_plot = (1,11,0)
x = [0]
righty = [0]
forwardy = [0]
lefty = [0]
epsilony = [1]

confidence_threshold = 200
host = 'localhost' 
port = 50000
backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((host,port)) 
s.listen(backlog)

client, address = s.accept() 
env = gym.make('UnityEnv-v0', unity_sim_client=client)
epsilon = 1
for episode in range(1, num_episodes+1):
    epsilon = np.power(1 - episode / num_episodes,2) * .75
    if episode == num_episodes:
        epsilon = 0
    epsilon = 0
    observation, _ = env.reset()
    terminated = False
    agent_loc = get_agent_space(observation)
    print("Doing episode " + str(episode))
    episode_return = 0
    while not terminated:
        
        action = None
        if get_confidence_in_state(agent_loc) < confidence_threshold:
            client.send("h".encode())
            wait_control_ack = client.recv(size)
            action = -1
        else:
            action = get_greedy_action(agent_loc, epsilon)
        
        observation, reward, terminated, _, _ = env.step(action)
        episode_return += reward
        q_visit_count[agent_loc[0]][agent_loc[1]][agent_loc[2]][action] += 1

        new_agent_loc = get_agent_space(observation)
        _, best_score = get_best_action_from(new_agent_loc)
        old_q_value = q_table[agent_loc[0]][agent_loc[1]][agent_loc[2]][action]
        q_table[agent_loc[0]][agent_loc[1]][agent_loc[2]][action] = old_q_value + alpha * (reward + gamma * best_score - old_q_value)
        agent_loc = new_agent_loc
    
    x.append(episode)
    forwardy.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][0])
    righty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][1])
    lefty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][2])
    epsilony.append(epsilon)

    if episode % 10 == 0:
        np.save("models/qtable", q_table)
        np.save("models/qvisitcount", q_visit_count)

        with open('models/tabular_training_progress.csv','a') as fd:
            fd.write(','.join([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(episode), str(epsilon), str(episode_return)]) + '\n')


print("Doing some stuff to figure out what epsilon decay, alpha, and episode count to use")
figure, axis = plt.subplots(1, 2)
axis[0].plot(x, righty, color = 'blue')
axis[0].plot(x, lefty, color = 'red')
axis[0].plot(x, forwardy, color = 'green')
axis[1].plot(x, epsilony, color = 'purple')
plt.show()

print("The answer for 3(i)a:")
print_policy()
print("")
print("The answer for 3(i)b:")
print_best_q_grid()