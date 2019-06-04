import os
import shutil
import pyarrow.plasma as plasma

def cond_mkdir(path):
    """
    Mkdir if not exists
    :param path:
    :return:
    """
    if not os.path.isdir(path):
        os.mkdir(path)

def refresh_tree(path):
    """
    When finished, brand new directory root at path
        Whether or not it used to exist and was empty
    :param path:
    :return:
    """
    cond_rmdir(path)
    os.mkdir(path)

def cond_rmdir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def id_gen(num):
    out = str(num)
    # if len(out) == 20 and out == "9"*20:
    #
    # need some error handling in case number of objects exceeds 10^20
    while len(out) < 20:
        out = "0" + out
    return plasma.ObjectID(out.encode())
    #  error handling could be as simple as clearing the plasma store and taking the mod of the current count

