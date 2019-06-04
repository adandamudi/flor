import cloudpickle
from flor.constants import *
import pyarrow.plasma as plasma
from flor.utils import id_gen
import json

def writer(file):
    """Writes everything received from plasma onto disk using cloudpickle"""
    counter = 1  # must start with at least 1

    client = plasma.connect(PLASMA_LOC)
    killcode = plasma.ObjectID(b"stop" * 5)
    with open(file, "a") as f:
        while 1:
            k = id_gen(counter)
            if client.contains(k):
                item = client.get(k)
                # if isinstance(item, bytes):
                #      data = cloudpickle.loads(item)
                # else:
                #     data = item
                try:
                    f.write(json.dumps(item) + '\n')
                except:
                    # f.write(json.dumps(cloudpickle.loads(item)) + '\n')
                    f.write(str(item) + '\n')
                counter += 1
            else:
                # if client does not contain the next key but it contains the killcode,
                # it is time to stop
                if client.contains(killcode):
                    return
