from flor.stateful import get, put
from flor.constants import *

class Controller:

    def __init__(self, init_in_func_ctx=True):
        """
        Corrected
        :param init_in_func_ctx:
        """
        self.depth_limit_mem = None
        self.depth_limit = get('depth_limit')
        if self.depth_limit is not None and init_in_func_ctx:
            self.depth_limit -= 1
            put('depth_limit', self.depth_limit)

    def do(self, d):
        prev_depth_limit = self.depth_limit

        if 'end_function' in d:
            if self.depth_limit is not None:
                self.depth_limit += 1
                put('depth_limit', self.depth_limit)

        if prev_depth_limit is not None and prev_depth_limit < 0:
            return Exit
        else:
            return Continue

    def get_license_to_serialize(self):
        return self.depth_limit is None or self.depth_limit >= 0

    def cond_inf_recursion_block(self):
        if self.get_license_to_serialize():
            self.depth_limit_mem = self.depth_limit
            self.depth_limit = -1
            put('depth_limit', self.depth_limit)
            return True
        return False
    
    def inf_recursion_unblock(self, past_block_succeeded):
        if past_block_succeeded:
            self.depth_limit = self.depth_limit_mem
            self.depth_limit_mem = None
            put('depth_limit', self.depth_limit)
