#!/usr/bin/env python3

import os
from multiprocessing import SimpleQueue

# Global log object for append.
FLOR_DIR = os.path.join(os.path.expanduser('~'), '.flor')
FLOR_SHARE = os.path.join('usr', 'share', 'flor')
FLOR_CUR = os.path.join(FLOR_DIR, '.current')
MODEL_DIR = os.path.join(FLOR_DIR, '.stateful')
MAX_PROC = 1

class Null: pass
class Exit: pass
class Continue: pass

global pids
pids = []
q = SimpleQueue()