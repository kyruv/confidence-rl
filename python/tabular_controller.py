import gym
import numpy as np
import matplotlib.pyplot as plt

# row, column, action
q_table = np.zeros([4,4,4])

# hyperparams
alpha = .01
num_episodes = 15000
gamma = .9

# make it deterministic
np.random.seed(1)

def get_greedy_action(state, epsilon):
    if np.random.uniform(0,1) < epsilon:
        return np.random.choice(4, 1)[0]
    
    best_action, _ = get_best_action_from(state)
    
    return best_action

def get_agent_loc(observation):
    return (observation['agent'][0], observation['agent'][1])

def get_best_action_from(state):
    best_action = None
    best_score = None
    for action in range(4):
        action_score = q_table[state[0]][state[1]][action]
        if best_score == None or action_score > best_score:
            best_score = action_score
            best_action = action
    return best_action, best_score

def print_policy():
    policy_print = [[""] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            best_action, _ = get_best_action_from((row,col))
            repr = "-"
            if best_action == 0:
                repr = "v"
            elif best_action == 1:
                repr = ">"
            elif best_action == 2:
                repr = "^"
            else:
                repr = "<"
            policy_print[row][col] = repr
            
    policy_print[0][3] = "-"
    policy_print[1][3] = "-"
    policy_print[1][1] = "-"
    print('\n'.join(' '.join(str(x) for x in row) for row in policy_print))
    
def print_best_q_grid():
    best_q_grid = [[""] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            _, best_score = get_best_action_from((row,col))
            best_q_grid[row][col] = "{:.5f}".format(best_score)
            
    print('\n'.join(' '.join(str(x) for x in row) for row in best_q_grid))

cell_to_plot = (1,0)
x = [0]
downy = [0]
righty = [0]
upy = [0]
lefty = [0]
epsilony = [1]

env = gym.make('UnityEnv-v0', unity_sim_client=None)
epsilon = 1
for episode in range(1, num_episodes+1):
    epsilon = np.power(1 - episode / num_episodes,5)
    if episode == num_episodes:
        epsilon = 0
    observation, _ = env.reset()
    terminated = False
    agent_loc = get_agent_loc(observation)
    
    while not terminated:
        action = get_greedy_action(agent_loc, epsilon)
        observation, reward, terminated, _, _ = env.step(action)
        new_agent_loc = get_agent_loc(observation)
        _, best_score = get_best_action_from(new_agent_loc)
        old_q_value = q_table[agent_loc[0]][agent_loc[1]][action]
        q_table[agent_loc[0]][agent_loc[1]][action] = old_q_value + alpha * (reward + gamma * best_score - old_q_value)
        agent_loc = new_agent_loc
    
    x.append(episode)
    downy.append(q_table[cell_to_plot[0]][cell_to_plot[1]][0])
    righty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][1])
    upy.append(q_table[cell_to_plot[0]][cell_to_plot[1]][2])
    lefty.append(q_table[cell_to_plot[0]][cell_to_plot[1]][3])
    epsilony.append(epsilon)


print("Doing some stuff to figure out what epsilon decay, alpha, and episode count to use")
figure, axis = plt.subplots(1, 2)
axis[0].plot(x, righty, color = 'blue')
axis[0].plot(x, lefty, color = 'red')
axis[0].plot(x, upy, color = 'green')
axis[0].plot(x, downy, color = 'black')
axis[1].plot(x, epsilony, color = 'purple')
plt.show()

print("The answer for 3(i)a:")
print_policy()
print("")
print("The answer for 3(i)b:")
print_best_q_grid()