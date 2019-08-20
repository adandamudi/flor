from flor.constants import *
import os
import json
import pickle as cloudpickle
from .serial_wrapper import *

class Flog:

    serializing = False
    depth_limit = None

    xp_name = None
    log_path = None

    buffer = []
    fork_now = False

    def __init__(self):
        self.writer = open(Flog.log_path, 'a')

    def write(self, s):
        Flog.buffer.append(s)
        buffer_len = len(Flog.buffer)
        if buffer_len >= BUF_MAX or Flog.fork_now:
            Flog.fork_now = False
            pid = os.fork()
            if not pid:
                Flog.serializing = True
                writer = open(str(os.getpid())+'.txt', 'a')
                for each in Flog.buffer:
                    try:
                        serialized = Flog.serialize_dict(each)
                    except:
                        serialized = "ERROR: failed to serialize"
                    finally:
                        writer.write(json.dumps(serialized) + '\n')
                writer.close()
                Flog.serializing = False #this is probably unnecessary since we're terminating immediately afterwards
                os._exit(0)
            else:
                Flog.buffer = []
        return True

    def serialize(self, x, name: str = None):
        try:
            Flog.serializing = True
            return SerialWrapper(x.copy())
        except:
            return SerialWrapper(x)
        finally:
            Flog.serializing = False

    def serial_write(self, s):
        self.writer.write(json.dumps(s) + '\n')
        self.writer.flush()
        return True

    def serial_serialize(self, x, name: str = None):
        try:
            Flog.serializing = True
            out = str(cloudpickle.dumps(x))
            return out
        except:
            return "ERROR: failed to serialize"
        finally:
            Flog.serializing = False

    @staticmethod
    def flagged(option: str = None):
        experiment_is_active = Flog.xp_name is not None
        if not experiment_is_active:
            return False
        if Flog.serializing:
            # Stack overflow avoidance
            return False

        # There is an active experiment and no risk of stack overflow

        depth_limit = Flog.depth_limit

        if option == 'start_function':
            # If flagged() reduces the depth below zero, we don't want the next expression to run
            # So we update the local depth_limit
            if Flog.depth_limit is not None:
                Flog.depth_limit -= 1
                depth_limit = Flog.depth_limit
        elif option == 'end_function':
            # If flagged() increases the depth to zero, this effect should be visible to the next call of flagged() but not this one
            # Since the update should happen after the full evaluation of the boolean expression
            # So we don't update the local depth_limit
            # The guarantee: either all flog statements in a function run or none do.
            if Flog.depth_limit is not None:
                Flog.depth_limit += 1
        return depth_limit is None or depth_limit >= 0

    @staticmethod
    # TODO: handle loop detection somewhere in here
    def serialize_dict(x):
        for k, v in x.items():
            if isinstance(x[k], SerialWrapper):
                x[k] = x[k].serialize()
            elif isinstance(x[k], dict):
                x[k] = Flog.serialize_dict(x[k])
            elif isinstance(x[k], list):
                x[k] = Flog.serialize_list(x[k])
        return x

    @staticmethod
    def serialize_list(x):
        for i in range(len(x)):
            if isinstance(x[i], SerialWrapper):
                x[i] = x[i].serialize()
            elif isinstance(x[i], dict):
                x[i] = Flog.serialize_dict(x[i])
            elif isinstance(x[i], list):
                x[i] = Flog.serialize_list(x[i])
        return x
