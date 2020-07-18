from flor.initializer import transform
transform()
del transform

from flor.initializer import initialize_wrapper, initialize, is_initialized
import flor.utils as utils
from flor.transformer import Transformer


import torch
from torch import cuda

try:
    if cuda.is_available() and not cuda.is_initialized():
        cuda.init()
except:
    if cuda.is_available() and not torch.distributed.is_initialized():
        cuda.init()

class NotInitializedError(RuntimeError):
    pass


def foo(*args, **kwargs):
    raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")


class NullClass:
    def __init__(self, *args, **kwargs):
        raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")

    @staticmethod
    def new():
        raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")

    @staticmethod
    def peek():
        raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")

    @staticmethod
    def pop():
        raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")

    @staticmethod
    def test_force(*args):
        raise NotInitializedError("[FLOR] Missing experiment name, mode, and memo.")


pin_state = foo
random_seed = foo
flush = foo
partition = foo
get_epochs = foo
sample = foo
SKIP = False
PID = None
NPARTS = None
RATE = None
SkipBlock = NullClass

namespace_stack = NullClass
skip_stack = NullClass

user_settings = None

initialize_wrapper()
del initialize_wrapper

__all__ = ['pin_state',
           'random_seed',
           'flush',
           'SKIP',
           'SkipBlock',
           'initialize',
           'is_initialized',
           'user_settings',
           'utils',
           'Transformer',
           'partition',
           'get_epochs',
           'PID',
           'NPARTS',
           'RATE',
           'sample'
           ]
