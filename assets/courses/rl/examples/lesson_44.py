import numpy as np
q = np.array([0., 2.])
for alpha in [.1, .5, 1., 2.]:
    z = q/alpha
    weight = np.exp(z-z.max())
    p = weight/weight.sum()
    entropy = -np.sum(p*np.log(p))
    regularized = p@q+alpha*entropy
    soft_value = alpha*(z.max()+np.log(weight.sum()))
    print("alpha",alpha,"policy",p,"reward",p@q,"H",entropy,"soft V",soft_value)
    assert np.isclose(regularized,soft_value)
