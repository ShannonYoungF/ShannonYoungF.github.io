import numpy as np
def softmax(q):
    z = np.exp(q-q.max()); return z/z.sum()
for alpha in [0.0, 0.5, 2.0]:
    q = np.array([0.0, 5.0])
    for _ in range(1000):
        # Logged action is A with deterministic reward 1.
        grad = np.array([2*(q[0]-1), 0.0])
        # Gradient of logsumexp(q)-q[A].
        grad += alpha*(softmax(q)-np.array([1.0, 0.0]))
        q -= 0.02*grad
    print("alpha", alpha, "Q", q, "chosen", ["A", "B"][q.argmax()])
print("True reward of B is unidentifiable from this dataset.")
