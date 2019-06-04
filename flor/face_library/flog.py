from flor.constants import *
from flor.utils import id_gen
from .controller import Controller
from .serial_wrapper import SerialWrapper
# from sklearn.base import is_classifier, is_regressor, is_outlier_detector
import os
# import json
import pickle as cloudpickle
import pyarrow.plasma as plasma

class Flog:

    """
    This class is instantiated only within a function

    ...
    That's a problem, we need this class, or equivalent
    To be instantiated in the header of client-side code
    even outside the scope of the function

    What behavior do we care about?

    """

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
        # self.writer = open(self.__get_current__(), 'a')
        self.controller = Controller(init_in_func_ctx)
        self.counter = 0
        self.store = client

    # def get_counter(self):
    #     """
    #     Returns counter and increments
    #     :return: counter
    #     """
    #     global counter
    #     current = counter
    #     counter += 1
    #     return current

    def write(self, s):
        if self.init_in_func_ctx:
            decision = self.controller.do(s)
            if decision is Exit:
                return False
        global counter
        try:
            self.store.put(s, id_gen(counter))
        except:
            try:
                self.store.put(self.serialize_dict(s), id_gen(counter))
            except:
                self.store.put("ERROR: Failed to serialize", id_gen(counter))
        counter += 1
        # self.writer.write(json.dumps(s) + '\n')
        # self.flush()
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

    # def can_plasma(self, x):
    #     """
    #     Determines whether plasma can serialize and store the object. Right now, this simply
    #     returns True.
    #     :param x:
    #     :return: True or False
    #     """
    #     # if is_classifier(x) or is_regressor(x) or is_outlier_detector(x):
    #     #     return False
    #     return True

    def serialize(self, x):
        # We need a license because Python evaluates arguments before calling a function
        if self.init_in_func_ctx:
            license = self.controller.get_license_to_serialize()
            if not license:
                return "PASS"
        return SerialWrapper(x)

    @staticmethod
    def __get_current__():
        name = os.listdir(FLOR_CUR).pop()
        return os.path.join(FLOR_DIR, name, 'log.json')

    @staticmethod
    def flagged():
        return not not os.listdir(FLOR_CUR)