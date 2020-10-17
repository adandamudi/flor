import os

from .iterator import it
from .skipblock import SkipBlock
from . import stateful

# TODO: Enable path override for flor directory
os.path.isdir('.flor') or os.mkdir('.flor')


def init(mode='record', memo=None, pid=None, nparts=None):
    assert mode in ['record', 'replay']
    stateful.MODE = mode
    stateful.MEMO = memo
    stateful.PID = pid
    stateful.NPARTS = nparts


__all__ = ['init', 'it', 'SkipBlock']
