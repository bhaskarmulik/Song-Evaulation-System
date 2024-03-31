############Code 1#######################
import numpy as np

# Assuming 'data' is your speech signal array and 'fs' is the sampling frequency
frame_size = 0.32  # 320 ms
overlap = 0.5
frame_samples = int(frame_size * fs)
step_size = int(frame_samples * (1 - overlap))

# Function to compute the Lp norm
def lp_norm(data, p):
    return (np.sum(np.abs(data)**p))**(1/p)

# Compute the L6 norm over split-second intervals
l6_norms = []
for i in range(0, len(data) - frame_samples + 1, step_size):
    frame = data[i:i+frame_samples]
    l6_norm = lp_norm(frame, 6)
    l6_norms.append(l6_norm)

# Compute the L2 norm over all split-second L6 norms
l2_norm_over_l6 = lp_norm(np.array(l6_norms), 2)

print(f'L6 norms over split-second intervals: {l6_norms}')
print(f'L2 norm over all split-second L6 norms: {l2_norm_over_l6}')


##############Code 2###########################