from flor.constants import *
from flor.face_library.flog import Flog
from flor.utils import cond_mkdir, refresh_tree, cond_rmdir
from flor.stateful import get, put, start
from flor.logs_manipulator import logger
import os
import datetime
import json
import multiprocessing
import pyarrow.plasma as plasma

class OpenLog:

    def __init__(self, name, depth_limit=0):
        start()
        self.name = name
        cond_mkdir(os.path.join(FLOR_DIR, name))
        refresh_tree(FLOR_CUR)
        open(os.path.join(FLOR_CUR, name), 'a').close()

        log_file = open(Flog.__get_current__(), 'a')

        if depth_limit is not None:
            put('depth_limit', depth_limit)

        session_start = {'session_start': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        log_file.write(json.dumps(session_start) + '\n')
        log_file.flush()
        log_file.close()

        # new code
        self.store = plasma.connect(PLASMA_LOC)
        self.store.evict(self.store.store_capacity())  # evicts everything in plasma
        # self.q = multiprocessing.Queue()  # need a queue to transmit last known ID, otherwise plasma hangs
        self.p2 = multiprocessing.Process(target=logger.writer, args=(Flog.__get_current__(),))
        self.p2.start()
        # end new code

    def exit(self):
        # begin new code
        self.killcode()
        # self.q.put(counter)
        self.p2.join() # waits for the process to finish before writing the ending
        # self.q.close()
        # self.q.join_thread()
        # end new code
        log_file = open(Flog.__get_current__(), 'a')
        session_end = {'session_end': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        log_file.write(json.dumps(session_end) + '\n')
        log_file.flush()

        refresh_tree(FLOR_CUR)
        cond_rmdir(MODEL_DIR)

        log_file.close()

    def killcode(self):
        stop = plasma.ObjectID(b"stop"*5)
        self.store.put("stop", stop)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()