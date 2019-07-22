from flor.constants import *
from flor.face_library.flog import Flog
from flor.utils import cond_mkdir, refresh_tree, cond_rmdir
from flor.stateful import get, put, start
import os
import datetime
import json
import signal

class OpenLog:

    def __init__(self, name, depth_limit=0):
        start()
        self.name = name
        cond_mkdir(os.path.join(FLOR_DIR, name))
        refresh_tree(FLOR_CUR)
        open(os.path.join(FLOR_CUR, name), 'a').close()
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        log_file = open(Flog.__get_current__(), 'a')

        if depth_limit is not None:
            put('depth_limit', depth_limit)

        session_start = {'session_start': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        log_file.write(json.dumps(session_start) + '\n')
        log_file.flush()
        log_file.close()

    def exit(self):
        # if Flog.buffer:
        Flog.buffer.append({'session_end': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))})
        pid = os.fork()
        if not pid:
            log_file = open(Flog.__get_current__(), 'a')
            for each in Flog.buffer:
                log_file.write(json.dumps(Flog.serialize_dict(each)) + '\n')
            log_file.flush()
            refresh_tree(FLOR_CUR)
            cond_rmdir(MODEL_DIR)
            log_file.close()
            os._exit(0)
            print("hehe")
        # else:
        #     log_file = open(Flog.__get_current__(), 'a')
        #     session_end = {'session_end': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        #     log_file.write(json.dumps(session_end) + '\n')
        #     log_file.flush()
        #
        #     refresh_tree(FLOR_CUR)
        #     cond_rmdir(MODEL_DIR)
        #
        #     log_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()