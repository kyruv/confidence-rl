import gym
import gym_envs
import numpy as np
import matplotlib.pyplot as plt
import socket
from datetime import datetime
import time
import random
import math

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

# stats-based confidence params
history_length = 20
num_samples = 15
block_length = 3
conf_m = history_length // block_length

# if you need to define for the first time use this
# q_value_history = np.zeros([5,12,8,3,history_length])
# q_value_history.fill(np.nan)
# for r in range(5):
#     for c in range(12):
#         for rot in range(8):
#             for a in range(3):
#                 q_value_history[0] = 0
q_value_history = np.load("models/qvaluehistory.npy")

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

def is_confident_in_state(state, alpha_threshold):
    # alpha threshold is confidence level, as in (1.0 - alpha)% confident
    act, q_compare = get_best_action_from(state)
    q_vals = q_value_history[state[0]][state[1]][state[2]][act]

    # fewer than 20 examples of this state - assume we aren't confident about it
    if np.isnan(q_vals).any():
        return False

    sample_avgs = []

    # this for-loop might work bc it's discrete, so the block-related stuff might not matter
    # for n in range(num_samples):
    #     sample = random.choice(q_vals, conf_m) # samples with replacement
    #     sample_avgs.append(sample.sum() / len(sample))

    # this is how the algorithm is specified for continous spaces
    for n in range(num_samples):
        # randomly sample "M" blocks
        sampled_blocks = []
        for m in range(conf_m):
            start = random.randrange(0, history_length - block_length)
            for b in range(block_length):
                sampled_blocks.append(q_vals[start + b])

        sample_avg = sum(sampled_blocks) / len(sampled_blocks)

        sample_avgs.append(sample_avg)

    sample_avgs.sort()

    temp = (num_samples * alpha_threshold / 2) + ((alpha_threshold + 2) / 6)
    j = math.floor(temp)
    r = temp - j

    T_a = (1 - r) * sample_avgs[j] + r * sample_avgs[j+1]
    upper_conf_bnd = 2 * (q_vals.sum() / len(q_vals)) - T_a
    print(f"T={T_a}, UCB={upper_conf_bnd}, Q for act={q_compare}")
    return q_compare < upper_conf_bnd


# --------- RUN DETAIL CONFIG -----------
experiment_mode = True

# if in experiment mode
use_simple_confidence = False
time_per_robot_move = .5

simple_confidence_threshold = 240
statistical_conf_alpha = 1

# if in training mode
max_epsilon = .75
# --------- END RUN DETAILS ----------

cell_to_plot = (2,0,4)
x = [0]
righty = [0]
forwardy = [0]
lefty = [0]
epsilony = [1]
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
    epsilon = np.power(1 - episode / num_episodes,2) * max_epsilon
    if episode == num_episodes:
        epsilon = 0
    if experiment_mode:
        epsilon = .005
    
    observation, _ = env.reset()
    terminated = False
    agent_loc = get_agent_space(observation)
    print("Doing episode " + str(episode))
    episode_return = 0
    while not terminated:
        
        action = None

        # determine if human should take over
        if experiment_mode:
            is_confident = False
            if use_simple_confidence:
                is_confident = get_confidence_in_state(agent_loc) > simple_confidence_threshold
            else:
                is_confident = is_confident_in_state(agent_loc, statistical_conf_alpha)

            if is_confident:
                action = get_greedy_action(agent_loc, epsilon)
            else:
                client.send("h".encode())
                wait_control_ack = client.recv(size)
                action = -1                
        else:
            action = get_greedy_action(agent_loc, epsilon)
        
        observation, reward, terminated, _, _ = env.step(action)
        episode_return += reward

        new_agent_loc = get_agent_space(observation)
        _, best_score = get_best_action_from(new_agent_loc)

        # only make updates when doing training
        if not experiment_mode:
            # standard q learning update
            old_q_value = q_table[agent_loc[0]][agent_loc[1]][agent_loc[2]][action]
            updated_q_value = old_q_value + alpha * (reward + gamma * best_score - old_q_value)
            q_table[agent_loc[0]][agent_loc[1]][agent_loc[2]][action] = updated_q_value
            
            # simple confidence tracking
            q_visit_count[agent_loc[0]][agent_loc[1]][agent_loc[2]][action] += 1

            # statistical confidence tracking
            need_to_overwrite = True

            for i in range(len(q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action])):
                if np.isnan(q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action][i]):
                    q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action][i] = updated_q_value
                    need_to_overwrite = False
                    break
            
            # remove oldest history of the cell and place new value
            if need_to_overwrite:
                # move first (oldest) element to last
                q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action] = np.roll(q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action], -1, axis=0)
                # overwrite oldest q_table with newest
                q_value_history[agent_loc[0]][agent_loc[1]][agent_loc[2]][action][-1] = updated_q_value
        
        agent_loc = new_agent_loc

        if experiment_mode and time_per_robot_move > 0:
            time.sleep(time_per_robot_move)
    
    x.append(episode)
    forwardy.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][0])
    righty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][1])
    lefty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][cell_to_plot[2]][2])
    epsilony.append(epsilon)

    if not experiment_mode and episode % 10 == 0:
        np.save("models/qtable", q_table)
        np.save("models/qvisitcount", q_visit_count)
        np.save("models/qvaluehistory", q_value_history)

        with open('models/tabular_training_progress.csv','a') as fd:
            fd.write(','.join([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(episode), str(epsilon), str(episode_return)]) + '\n')


print("Doing some stuff to figure out what epsilon decay, alpha, and episode count to use")
figure, axis = plt.subplots(1, 2)
axis[0].plot(x, righty, color = 'blue')
axis[0].plot(x, lefty, color = 'red')
axis[0].plot(x, forwardy, color = 'green')
axis[1].plot(x, epsilony, color = 'purple')
plt.show()