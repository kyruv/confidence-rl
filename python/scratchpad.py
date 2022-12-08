import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns

def convert_M2_array(m2):
    count = m2[0]
    mean = m2[1]
    M2 = m2[2]
    if count < 2:
        return None
    else:
        (mean, variance, sampleVariance) = (mean, M2 / count, M2 / (count - 1))
        
        return np.array([mean, variance, sampleVariance])

# q_dist = np.load("models/qdistribution.npy")
# finalized = np.zeros(shape=q_dist.shape)

# for r in range(5):
#     for c in range(12):
#         for rot in range(8):
#             for action in range(3):
#                 finalized[r][c][rot][action] = convert_M2_array(q_dist[r][c][rot][action])

# stdev = finalized[:,:,:,:,2]

# count_actions_collapsed = np.sum(stdev, axis=3)
# print(count_actions_collapsed.shape)

# maxv = np.max(count_actions_collapsed)
# count_actions_collapsed[1,1,:] = maxv + 1
# count_actions_collapsed[0,3,:] = maxv + 1
# count_actions_collapsed[1,3,:] = maxv + 1
# count_actions_collapsed[3,3,:] = maxv + 1
# count_actions_collapsed[4,3,:] = maxv + 1
# count_actions_collapsed[2,6,:] = maxv + 1
# count_actions_collapsed[1,9,:] = maxv + 1
# count_actions_collapsed[2,9,:] = maxv + 1
# count_actions_collapsed[2,10,:] = maxv + 1
# count_actions_collapsed[3,10,:] = maxv + 1
# count_actions_collapsed[2,11,:] = maxv + 1

# count_rotations_collapsed = np.average(count_actions_collapsed, axis=2)

# print(count_actions_collapsed[1,1,:])

# fig, ax = plt.subplots( nrows=3, ncols=3, figsize=(16,8))
# cbar_ax = fig.add_axes([.91, .2, .03, .6])
# titles = [["Facing ↖", "Facing ↑", "Facing ↗"], ["Facing ←", "Averaged", "Facing →"], ["Facing ↙", "Facing ↓", "Facing ↘"]]
# rotation_keys = [[5,6,7], [4,-1,0], [3,2,1]]

# cmap = plt.cm.get_cmap('hot_r').copy()
# cmap.set_under('purple')
# cmap.set_over('grey')

# for r in range(3):
#     for c in range(3):
#         data = None
#         if r == 1 and c == 1:
#             data = count_rotations_collapsed
#         else:
#             data = count_actions_collapsed[:,:,rotation_keys[r][c]]

#         hm = sns.heatmap(data,
#                 # mask=np.isnan(data),
#                 ax=ax[r][c],
#                 # vmin=190, 
#                 # vmax=maxv,
#                 square=True,
#                 cmap = cmap,
#                 cbar=(r,c) == (0,0),
#                 cbar_ax=cbar_ax)
#         hm.invert_yaxis()
#         ax[r][c].set_title(titles[r][c])

# fig.tight_layout(rect=[0, 0, .9, 1])
# plt.show()


# all_stds = np.sort(finalized[:,:,:,:,2].flatten())

# plt.hist(all_stds, bins=10)
# plt.show()

# print(np.nanmax(all_stds))

def get_clear_action_score(q_table, r, c, rot):
    best_action = None
    best_score = None
    scores = np.sort(q_table[r][c][rot])
    
    return scores[-1] - scores[-2]

def get_best_action_from(q_table, r, c, rot):
    best_action = None
    best_score = None
    for action in range(3):
        action_score = q_table[r][c][rot][action]
        if best_score == None or action_score > best_score:
            best_score = action_score
            best_action = action
    return best_action, best_score

def get_policy(rotation):
    q_table = np.load("models/qtable.npy")
    policy = np.zeros([5,12], dtype='object')

    action_repr = ["F", "R", "L"]

    for r in range(5):
        for c in range(12):
            if count_actions_collapsed[r][c][0] == maxv + 1:
                policy[r][c] = ""
            else:
                best_action, _ = get_best_action_from(q_table, r, c, rotation)
                policy[r][c] = action_repr[best_action]
    
    return policy





# q_visit_count = np.load("models/qepcount.npy")
# print(q_visit_count.mean())
# # print(q_visit_count[0,2,4,:])

# # q_history = np.load("models/qvaluehistory.npy")

q_table = np.load("models/qtable.npy")

data = np.zeros(shape=(5,12,8))

for r in range(5):
    for c in range(12):
        for rot in range(8):
            data[r][c][rot] = get_clear_action_score(q_table, r, c, rot)

count_actions_collapsed = data
print(count_actions_collapsed.shape)

maxv = np.max(count_actions_collapsed)
count_actions_collapsed[1,1,:] = maxv + 1
count_actions_collapsed[0,3,:] = maxv + 1
count_actions_collapsed[1,3,:] = maxv + 1
count_actions_collapsed[3,3,:] = maxv + 1
count_actions_collapsed[4,3,:] = maxv + 1
count_actions_collapsed[2,6,:] = maxv + 1
count_actions_collapsed[1,9,:] = maxv + 1
count_actions_collapsed[2,9,:] = maxv + 1
count_actions_collapsed[2,10,:] = maxv + 1
count_actions_collapsed[3,10,:] = maxv + 1
count_actions_collapsed[2,11,:] = maxv + 1

count_rotations_collapsed = np.average(count_actions_collapsed, axis=2)

fig, ax = plt.subplots( nrows=3, ncols=3, figsize=(16,8))
cbar_ax = fig.add_axes([.91, .2, .03, .6])
titles = [["Facing ↖", "Facing ↑", "Facing ↗"], ["Facing ←", "Averaged", "Facing →"], ["Facing ↙", "Facing ↓", "Facing ↘"]]
rotation_keys = [[5,6,7], [4,-1,0], [3,2,1]]

cmap = plt.cm.get_cmap('YlOrRd').copy()
cmap.set_under('white')
cmap.set_over('grey')

for r in range(3):
    for c in range(3):
        data = None
        if r == 1 and c == 1:
            data = count_rotations_collapsed
        else:
            data = count_actions_collapsed[:,:,rotation_keys[r][c]]

        policy_labels = [[""] * 12 for _ in range(5)]
        if not (r == 1 and c == 1):
            policy_labels = get_policy(rotation_keys[r][c])

        hm = sns.heatmap(data, 
                ax=ax[r][c],
                annot = policy_labels,
                vmin=np.percentile(count_actions_collapsed, 15), 
                fmt = '',
                linewidths=.5, 
                linecolor='black',
                annot_kws={"fontsize":7},
                # norm=LogNorm(vmin=np.percentile(count_actions_collapsed, 15), vmax=maxv),
                vmax=maxv,
                square=True,
                cmap = cmap,
                cbar=(r,c) == (0,0),
                cbar_ax=cbar_ax)
        hm.invert_yaxis()
        ax[r][c].set_title(titles[r][c])

fig.tight_layout(rect=[0, 0, .9, 1])
# cbar = ax[2][3].figure.colorbar(im, 
#                           ax = ax[1][3],
#                           shrink=0.5 )
# ax[1][1].set_title("ALL Directions")
plt.show()

# print(q_visit_count.mean())
# print(q_visit_count.std())
# print(q_visit_count.max())

# print(q_history)

# plt.hist(q_visit_count.flatten(), bins=100)
# plt.show()