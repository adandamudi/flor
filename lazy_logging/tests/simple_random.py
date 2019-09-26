import numpy as np
import random

x = np.random.randint(0, 9)
y = random.randint(0,9)

z = random.randint(0, 9)
z = (lambda p, q: random.randint(p,q) + 1)
z += random.randint(0, 9)
