import math
import os
import sys
import shutil
import flor.common.copy
from flor.constants import *

class PATH:
    def __init__(self, root_path, path_from_home):
        root_path = '~' if root_path is None else root_path
        self.path_from_home = path_from_home
        self.squiggles = os.path.join(root_path, path_from_home)
        if root_path == '~':
            self.absolute = os.path.join(os.path.expanduser('~'), path_from_home)
        else:
            self.absolute = os.path.join(os.path.abspath(root_path), path_from_home)


def cond_mkdir(path):
    """
    Mkdir if not exists
    :param path:
    :return:
    """
    if not os.path.isdir(path):
        os.mkdir(path)


def refresh_tree(path):
    """
    When finished, brand new directory root at path
        Whether or not it used to exist and was empty
    :param path:
    :return:
    """
    cond_rmdir(path)
    os.mkdir(path)


def cond_rmdir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def fprint(dir_tree_list, device_id):
    root_path = os.path.sep + os.path.join(*dir_tree_list)

    def write(s):
        with open(os.path.join(root_path, "flor_output_{}.txt".format(device_id)), 'a') as f:
            f.write(str(s) + '\n')

    return write

def get_partitions(num_epochs, num_partitions, pretraining, period):
    # Roundrobin allocation with pipelining
    assert num_partitions <= num_epochs
    if pretraining:
        del period
        partitions = [[] for _ in range(num_partitions)]
        for epoch in range(num_epochs):
            partitions[epoch % num_partitions].append(-1)
        i = 0
        for j in range(num_partitions):
            for k in range(len(partitions[j])):
                partitions[j][k] = i
                i += 1
        assert i == num_epochs
        for part in partitions:
            for each in part:
                assert each >= 0
        assert partitions[-1][-1] == num_epochs - 1
        return partitions
    else:
        range_regions = []
        i = 0
        while i*period < num_epochs:
            start = i*period
            stop = min((i+1)*period, num_epochs)
            range_regions.append(range(start, stop))
            i+=1
        partitions = [[] for _ in range(num_partitions)]
        for range_element in range(len(range_regions)):
            #roundrobin work allocation, early epochs first
            partitions[range_element % num_partitions].append(-1)
        for j in range(num_partitions):
            for k in range(len(partitions[j])):
                partitions[j][k] = range_regions.pop(0)
        assert len(range_regions) == 0
        partitions = [range(rs[0].start, rs[-1].stop) if rs else [] for rs in partitions]
        if num_partitions < num_epochs:
            return partitions
        else:
            # For when you sample a Fine-tuning run with sparse checkpoints
            return [range(p.start, s+1) for p in partitions for s in p]

def deepcopy_cpu(x):
    return flor.common.copy.deepcopy(x)

def parse_args(filter_flor):
    if [each for each in sys.argv if '--flor' == each[0:len('--flor')]]:
        # Fetch the flags we need without disrupting user code
        flor_settings = {
            'mode': ['exec', 'reexec'], # default: exec
            'predinit': ['weak', 'strong'],
            'name': ANY,
            'memo': ANY,
            'maxb': ANY,  # buffer limit
            'rd': ANY,     # root directory for .flor subdir,
            'sd': ANY,      # source directory for transformation
            'pid': ANY,     # partition id, for parallelism
            'ngpus': ANY,   # num_gpus, for parallelism
            'rate': ANY     # sampling rate
        }

        argvs = []
        flor_arg = None
        for each in sys.argv:
            if '--flor' != each[0:len('--flor')]:
                argvs.append(each)
            else:
                flor_arg = each.split('=')[1]
                assert flor_arg != '', "[FLOR] Enter a setting and value: {}".format(flor_settings)
        if filter_flor:
            sys.argv = argvs

        user_settings = {}

        # Validate the user entered valid settings
        flor_arg = flor_arg.split(',')
        flor_arg = [each.split(':') for each in flor_arg]
        for (k, v) in flor_arg:
            assert k in flor_settings, "[FLOR] Invalid setting: {}".format(k)
            assert flor_settings[k] is ANY or v in flor_settings[k], "[FLOR] Invalid value for setting `{}`. Value must be one of {}".format(k, flor_settings[k])
            assert k not in user_settings, "[FLOR] Duplicate setting entered: {}".format(k)
            user_settings[k] = v

        # Check that required flags are set
        assert 'name' in user_settings, "[FLOR] Missing required parameter: name."
        return user_settings