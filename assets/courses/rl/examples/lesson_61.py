import numpy as np
def normal_logp(z): return -0.5*z*z-0.5*np.log(2*np.pi)
def stable_log_jacobian(z):
    return 2*(np.log(2)-z-np.logaddexp(0, -2*z))
z = np.array([0.0, 1.0, 10.0])
for scale in [1.0, 2.0]:
    logp = normal_logp(z)-stable_log_jacobian(z)-np.log(scale)
    assert np.isfinite(logp).all()
    print("action scale", scale, "transformed logp", logp)
assert np.isclose(normal_logp(0)-np.log(2), -1.612085713764618)
target = 1+0.9*(3-0.2*(-1))
assert np.isclose(target, 3.88)
print("critic target sign check:", target)
print("Next: python lesson_45.py --smoke")
print("Then repeat the fixed training budget over independent seeds.")
