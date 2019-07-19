from flor.constants import *
from .controller import Controller
import os
import json
import pickle as cloudpickle
import psutil
from flor.face_library.serial_wrapper import SerialWrapper
from numpy import ndarray
from pandas import DataFrame

class Flog:

    """
    This class is instantiated only within a function

    ...
    That's a problem, we need this class, or equivalent
    To be instantiated in the header of client-side code
    even outside the scope of the function

    What behavior do we care about?

    """
    buffer = []
    fork_now = False

    def __init__(self, init_in_func_ctx=True):
        """
        We have to read the current name of the experiment
        The log.json file in the corresponding directory need not exist in advance
        The Controller initialization
            Reads and modifies the depth limit automatically
            Because we assume we're in the context of a function

        Recommended Correction:
        Flagging -- On initialization, parameterize on context of initialization.

        Modification preserves intended behavior in previous context
        Generalizes
        On context outside function, no modification of depth limit

        """
        self.init_in_func_ctx = init_in_func_ctx
        self.writer = open(self.__get_current__(), 'a')
        self.controller = Controller(init_in_func_ctx)

    def serial_write(self, s):
        #TODO: Can I dump with json rather than dumps
        if self.init_in_func_ctx:
            decision = self.controller.do(s)
            if decision is Exit:
                return False
        self.writer.write(json.dumps(s) + '\n')
        self.flush()
        os._exit(0) #TODO: replace 0 with the correct signal
        # return True

    def write(self, s):
        if self.init_in_func_ctx:
            decision = self.controller.do(s)
            if decision is Exit:
                return False
        if len(Flog.buffer) >= BUF_MAX or Flog.fork_now:
            if Flog.fork_now:
                Flog.fork_now = False
            pid = os.fork()
            if not pid:
                for each in Flog.buffer:
                    self.writer.write(json.dumps(self.serialize_dict(each)) + '\n')
                os._exit(0)
            else:
                Flog.buffer = []
        Flog.buffer.append(s)
        return True

    def serialize_dict(self, x):
        for k, v in x.items():
            if isinstance(x[k], SerialWrapper):
                x[k] = x[k].serialize()
            elif isinstance(x[k], dict):
                x[k] = self.serialize_dict(x[k])
            elif isinstance(x[k], list):
                x[k] = self.serialize_list(x[k])
        return x

    def serialize_list(self, x):
        for i in range(len(x)):
            if isinstance(x[i], SerialWrapper):
                x[i] = x[i].serialize()
            elif isinstance(x[i], dict):
                x[i] = self.serialize_dict(x[i])
            elif isinstance(x[i], list):
                x[i] = self.serialize_list(x[i])
        return x

    def flush(self):
        self.writer.flush()

    def serialize(self, x):
        # We need a license because Python evaluates arguments before calling a function
        if self.init_in_func_ctx:
            license = self.controller.get_license_to_serialize()
            if not license:
                return "PASS"
        if isinstance(x, dict) or isinstance(x, list) or isinstance(x, set):
            return SerialWrapper(x.copy())
        if isinstance(x, ndarray) or isinstance(x, DataFrame):
            return SerialWrapper(x.copy())
        return SerialWrapper(x)

    @staticmethod
    def __get_current__():
        name = os.listdir(FLOR_CUR).pop()
        return os.path.join(FLOR_DIR, name, 'log.json')

    @staticmethod
    def flagged(option: str = None):
        if option == 'nofork':
            return not not os.listdir(FLOR_CUR)
        return not not os.listdir(FLOR_CUR)
        # if not not os.listdir(FLOR_CUR):
        #     pid = os.fork()
        #     if not pid:
        #         os.nice(1)
        #         return True
        #     else:
        #         return False
