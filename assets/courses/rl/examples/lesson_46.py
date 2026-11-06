import numpy as np
gamma = .9
def compare(distances):
    phi = -np.asarray(distances, dtype=float)
    T = len(phi)-1
    reward = np.zeros(T)
    reward[-1] = 10  # terminal goal has phi=0
    shaping = gamma*phi[1:]-phi[:-1]
    weights = gamma**np.arange(T)
    original = weights@reward
    shaped = weights@(reward+shaping)
    print(distances, "original", original, "shaped", shaped, "shift",shaped-original)
    assert np.isclose(shaped-original, -phi[0])
compare([3,2,1,0])
compare([3,2,3,2,1,0])
