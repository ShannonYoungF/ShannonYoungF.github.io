import numpy as np
g = np.array([1.0, 0.0])
F = np.diag([2.0, 1.0])
delta = 0.01
natural = np.linalg.solve(F, g)
step = np.sqrt(2*delta/(g@natural))*natural
print("step:", step)
print("quadratic KL:", 0.5*step@F@step)
def bernoulli_kl(p, q):
    return p*np.log(p/q)+(1-p)*np.log((1-p)/(1-q))
for dtheta in [0.2, 1.0, 2.0]:
    q = 1/(1+np.exp(-dtheta))
    print(dtheta, "actual", bernoulli_kl(.5,q), "quadratic", .5*.25*dtheta**2)
