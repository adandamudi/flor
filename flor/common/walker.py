from flor.transformer import Transformer

import os


class Walker:

    def __init__(self, rootpath, root_script):
        """
        :param rootpath: Absolute path we want to transform
        """
        self.rootpath = os.path.abspath(rootpath)
        self.root_script = os.path.abspath(root_script)

    def compile_tree(self):
        """
        We now do transformation in place
        :param lib_code:
        :return:
        """
        failed_transforms = []

        for (src_root, dirs, files) in os.walk(self.rootpath):
            # SRC_ROOT: in terms of Conda-Cloned environment
            pyfs = [os.path.join(src_root, f) for f in files if os.path.splitext(f)[1] == '.py']
            Transformer.transform(pyfs, inplace=True, root_script=self.root_script)