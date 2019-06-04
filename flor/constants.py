#!/usr/bin/env python3

import os
import pyarrow.plasma as plasma

# Global log object for append.
FLOR_DIR = os.path.join(os.path.expanduser('~'), '.flor')
FLOR_CUR = os.path.join(FLOR_DIR, '.current')
MODEL_DIR = os.path.join(FLOR_DIR, '.stateful')
PLASMA_LOC = '/tmp/plasma'

class Null: pass
class Exit: pass
class Continue: pass


global counter
global client
counter = 0
client = plasma.connect(PLASMA_LOC)