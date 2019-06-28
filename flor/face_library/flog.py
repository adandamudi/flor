from flor.constants import *
from .controller import Controller
import os
import json
import pickle as cloudpickle

class Flog:

    """
    This class is instantiated only within a function

    ...
    That's a problem, we need this class, or equivalent
    To be instantiated in the header of client-side code
    even outside the scope of the function

    What behavior do we care about?

    """
    one_and_done = False

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
        if os.nice(0) == 2:
            os._exit(0)
        self.init_in_func_ctx = init_in_func_ctx
        self.writer = open(self.__get_current__(), 'a')
        self.controller = Controller(init_in_func_ctx)

    def write(self, s):
        if os.nice(0) != 2:
            return True
        #TODO: Can I dump with json rather than dumps
        with lock:
            if self.init_in_func_ctx:
                decision = self.controller.do(s)
                if decision is Exit:
                    return False
            self.writer.write(json.dumps(s) + '\n')
            self.flush()
        os._exit(0) #TODO: replace 0 with the correct signal
        # return True

    def flush(self):
        self.writer.flush()

    def serialize(self, x):
        if os.nice(0) != 2:
            return
        # We need a license because Python evaluates arguments before calling a function
        if self.init_in_func_ctx:
            license = self.controller.get_license_to_serialize()
            if not license:
                return "PASS"
        try:

            out = str(cloudpickle.dumps(x))
            return out
        except:
            return "ERROR: failed to serialize"

    @staticmethod
    def __get_current__():
        name = os.listdir(FLOR_CUR).pop()
        return os.path.join(FLOR_DIR, name, 'log.json')

    @staticmethod
    def flagged():
        if not Flog.one_and_done:
            Flog.one_and_done = True
            return not not os.listdir(FLOR_CUR)

        if not os.fork():
            os.nice(2)
            if not not os.listdir(FLOR_CUR):
                return True
            else:
                os._exit(0)
        else:
            return False