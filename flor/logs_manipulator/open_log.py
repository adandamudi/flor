import datetime
import json
import re
import uuid
import os

import git
import signal

from flor.constants import *
from flor.face_library.flog import Flog
from flor.utils import cond_mkdir, refresh_tree, cond_rmdir, get_timestamp
from flor.versioner.versioner import Versioner


class OpenLog:

    def __init__(self, name, depth_limit=None):
        self.name = name
        cond_mkdir(os.path.join(FLOR_DIR, name))
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        Flog.xp_name = name
        Flog.log_path = os.path.join(FLOR_DIR, name, 'log.json')

        log_file = open(Flog.log_path, 'a')

        if depth_limit is not None:
            Flog.depth_limit = depth_limit

        session_start = {'session_start': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

        # MAC address
        MAC_addr = {'MAC_address': ':'.join(re.findall('..?', '{:x}'.format(uuid.getnode())))}
        session_start.update(MAC_addr)


        # Get EC2 instance type
        try:
            import boto3
            ec2 = boto3.resource('ec2')
            for i in ec2.instances.all():
                session_start.update({'EC2_instance_type': i.instance_type})
        except:
            session_start.update({'EC2_instance_type': 'None'})

        # User info from Git
        class GitConfig(git.Repo):
            def __init__(self, *args, **kwargs):
                #
                # Work around the GitPython issue #775
                # https://github.com/gitpython-developers/GitPython/issues/775
                #
                self.git_dir = os.path.join(Versioner.get_ancestor_repo_path(os.getcwd()), ".git")
                git.Repo.__init__(self, *args, **kwargs)

        r = GitConfig().config_reader()
        user_name = r.get_value('user', 'name')
        user_email = r.get_value('user', 'email')
        session_start.update({'git_user_name': user_name})
        session_start.update({'git_user_email': user_email})


        # System's userid
        import getpass
        user_id = getpass.getuser()
        session_start.update({'user_id': user_id})


        timestamp, local_time, utc_time, src_of_time = get_timestamp()

        session_start.update({'timestamp': timestamp})
        session_start.update({'local_time': local_time})
        session_start.update({'UTC_time': utc_time})
        session_start.update({'source_of_time': src_of_time})


        log_file.write(json.dumps(session_start) + '\n')

        log_file.flush()
        log_file.close()

    def exit(self):
        # log_file = open(Flog.log_path, 'a')
        session_end = {'session_end': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

        timestamp, local_time, utc_time, src_of_time = get_timestamp()
        session_end.update({'timestamp': timestamp})
        session_end.update({'local_time': local_time})
        session_end.update({'UTC_time': utc_time})
        session_end.update({'source_of_time': src_of_time})

        # log_file.write(json.dumps(session_end) + '\n')
        # log_file.flush()
        Flog.buffer.append(session_end)

        if Flog.buffer or Flog.fork_now:
            pid = os.fork()
            if not pid:
                Flog.serializing = True
                writer = open(Flog.log_path[:-8] + str(os.getpid()) + '.json', 'a')
                writer.write(json.dumps({'prev': Flog.prev_fork}) + '\n')
                for each in Flog.buffer:
                    try:
                        serialized = Flog.serialize_dict(each)
                    except:
                        serialized = "ERROR: failed to serialize"
                    finally:
                        writer.write(json.dumps(serialized) + '\n')
                writer.close()
                Flog.serializing = False  # this is probably unnecessary since we're terminating immediately afterwards
                # This is the final fork, it is likely that this will finish last. However, we should still do some detection
                self.merge()
                os._exit(0)

        cond_rmdir(MODEL_DIR)
        # log_file.close()

    def merge(self):
        import os
        import json

        os.chdir(Flog.log_path[:-8])
        log_files = []
        # do some filtering with the log files
        for each in os.listdir():
            if each[-4:] == 'json' and each != 'log.json':
                try:
                    num = int(each[:-5])
                    log_files.append(num)
                except ValueError:
                    continue

        log_files.sort()
        prev = None

        with open('log.json', 'a') as logger:
            for each in log_files:
                with open(str(each) + '.json', "r") as f:
                    x = f.readlines()
                    if json.loads(x[0])['prev'] != prev:
                        # do something here because this means that the file has not been written yet
                        pass
                    if len(x) < 50001:
                        print("corrupted data?")
                        pass
                    for each in x[1:]:
                        logger.write(json.dumps(each) + '\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()