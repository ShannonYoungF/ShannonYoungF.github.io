import numpy as np
state = 2.0
theta = .2
def value(parameter):
    action = parameter*state
    return -(action-1)**2
action = theta*state
gradient = state*(-2*(action-1))
h = 1e-6
check = (value(theta+h)-value(theta-h))/(2*h)
new_theta = theta+.1*gradient
print("action:", action, "gradient:", gradient, "finite difference:", check)
print("old Q:", value(theta), "new Q:", value(new_theta))
assert np.isclose(gradient, check)
