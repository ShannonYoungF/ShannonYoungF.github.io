"""Termination versus external truncation: an executable regression example."""
import numpy as np

def target(reward, next_value, terminated, truncated, gamma=0.9):
    # truncated deliberately does not enter the bootstrap mask.
    return reward + gamma * (not terminated) * next_value

if __name__ == '__main__':
    rng = np.random.default_rng(27)
    reward, next_value = 1.0, 5.0
    cases = [('normal', False, False), ('task terminal', True, False),
             ('external time limit', False, True), ('terminal at limit', True, True)]
    for name, terminal, cutoff in cases:
        good = target(reward, next_value, terminal, cutoff)
        wrong = reward + .9 * (not (terminal or cutoff)) * next_value
        print(f'{name:22s} correct={good:.1f} done-mask={wrong:.1f}')
    assert np.isclose(target(1, 5, False, True), 5.5)
    assert np.isclose(target(1, 5, True, False), 1.0)
    # A continuing reward-1 process has value 1/(1-gamma)=10.
    v_correct = v_wrong = 0.0
    for _ in range(10000):
        externally_cut = rng.random() < 0.2
        v_correct += .02 * (1 + .9*v_correct - v_correct)
        v_wrong += .02 * (1 + .9*(not externally_cut)*v_wrong - v_wrong)
    print('true continuing value: 10')
    print('correct bootstrap:', v_correct, 'wrong cutoff mask:', v_wrong)
    print('Reset collection after either flag, but never use the reset observation as next_state.')
