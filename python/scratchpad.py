import numpy as np
import matplotlib.pyplot as plt

q_visit_count = np.load("models/qvisitcount.npy")

q_history = np.load("models/qvaluehistory.npy")

print(q_visit_count.mean())
print(q_visit_count.std())
print(q_visit_count.max())

print(q_history)

# plt.hist(q_visit_count.flatten(), bins=100)
# plt.show()