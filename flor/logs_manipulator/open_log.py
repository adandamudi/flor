import datetime
import json
import re
import uuid

import git

from flor.constants import *
from flor.face_library.flog import Flog
from flor.stateful import put, start
from flor.utils import cond_mkdir, refresh_tree, cond_rmdir
from flor.utils import get_ntp_time


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
                self.git_dir = os.path.join(os.getcwd(), ".git")
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

        timestamp, local_time, utc_time = get_ntp_time()

        session_start.update({'timestamp': timestamp})
        session_start.update({'local_time': local_time})
        session_start.update({'UTC_time': utc_time})

        log_file.write(json.dumps(session_start) + '\n')

        log_file.flush()
        log_file.close()

    def exit(self):
        log_file = open(Flog.__get_current__(), 'a')
        session_end = {'session_end': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

        timestamp, local_time, utc_time = get_ntp_time()
        session_end.update({'timestamp': timestamp})
        session_end.update({'local_time': local_time})
        session_end.update({'UTC_time': utc_time})

        log_file.write(json.dumps(session_end) + '\n')
        log_file.flush()

        refresh_tree(FLOR_CUR)
        cond_rmdir(MODEL_DIR)

        log_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()