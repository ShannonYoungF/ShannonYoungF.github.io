"""Double DQN. Download lesson_26.py into this same directory first.
pip install numpy torch gymnasium; python lesson_28.py --smoke
"""
import numpy as np
from lesson_26 import parser, train

def selection_evaluation_demo():
    online = np.array([5.0, 4.0])
    target = np.array([2.0, 6.0])
    selected = int(online.argmax())
    print('online selects action:', selected)
    print('DQN bootstrap:', target.max())
    print('Double DQN bootstrap:', target[selected])
    print('reward=1, gamma=.9: DQN target=', 1+.9*target.max(),
          'Double DQN target=', 1+.9*target[selected])

if __name__ == '__main__':
    selection_evaluation_demo()
    train(parser(default_seed=28).parse_args(), double=True)
