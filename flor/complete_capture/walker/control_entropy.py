import os
import astor
import ast

class EntropyController:
    """
    First Approx: Code does not re-introduce entropy beyond initialization. <--
    Second Approx: Code may re-introduce entropy via default generators (re-seed)
    Third Approx: Code may re-introduce entropy via user initialized generators
    """

    def __init__(self):
        """
        :param rootpath: Absolute path we want to transform
        """
        # TODO: Get the transitive dependencies.

        # The following native Python libraries have random states:
        # Random: https://docs.python.org/3/library/random.html
        #        {set: [random.seed, random.setstate], get: [getstate]}
        # Flor won't be able to support the following: The functions supplied by this module are actually bound methods of a hidden instance of the random.Random class. You can instantiate your own instances of Random to get generators that don’t share state.
        #
        # os.urandom, os.getrandom: Crypto-strong: https://docs.python.org/3/library/os.html#os.urandom
        # No state to set... output value is cat of /dev/urandom, intercept always.
        #
        # secrets: https://docs.python.org/3/library/secrets.html#module-secrets

        # The following libraries have ways of capturing state directly.
        #
        # Numpy: {set: [numpy.random.seed, numpy.random.set_state, numpy.random.RandomState] , get: numpy.random.get_state}
        # Scipy: uses Numpy
        # Pandas: uses Numpy ==== uses com.random_state https://github.com/pandas-dev/pandas/blob/v0.25.1/pandas/core/generic.py#L4798-L4971 ... which is part of pandas.core.common --- which uses numpy.
        # Sklearn: uses Numpy
        # Tensorflow: tf.random https://www.tensorflow.org/api_docs/python/tf/random/set_random_seed
        #                   set-nested: tf.random.experimental ... (module, like np.random.RandomState)
        #                   get: get_seed
        #                   set: set_random_seed
        # Pytorch: https://pytorch.org/docs/stable/notes/randomness.html
        #           https://pytorch.org/docs/stable/torch.html#torch.manual_seed
        #          https://pytorch.org/docs/stable/_modules/torch/random.html
        #           https://pytorch.org/docs/stable/random.html
        #           remember torch.cuda.manual_seed too... https://pytorch.org/docs/stable/cuda.html#torch.cuda.manual_seed
        #
        # Torchvision: https://discuss.pytorch.org/t/non-reproducible-result-with-gpu/1831/5
        #
        # Keras: uses tf and np

        # TODO: Summary... random, numpy, tf, and torch are the sources of randomness in ML/DS.

        # There's some concept of a HEADER.
        # Then there is logging on certain events that introduce entropy into the program.

        numpy_random = {'numpy', 'random'}
        tf_numpy_random = {'tensorflow', } | numpy_random
        torch_numpy_random = {'torch',} | numpy_random

        self.entropy_dependencies = {
            'numpy': numpy_random,
            'scipy': numpy_random,
            'pandas': numpy_random,
            'statsmodels': numpy_random,
            'matplotlib': numpy_random,
            'seaborn': numpy_random,
            'plotly': numpy_random,
            'bokeh': numpy_random,
            'pydot': set([]),
            'sklearn': numpy_random,
            'xgboost': numpy_random,
            'lightgbm': numpy_random,
            'eli5': set([]),
            'tensorboard': tf_numpy_random,
            'tensorflow': tf_numpy_random,
            'tensorflow_estimator': tf_numpy_random,
            'torch': torch_numpy_random,
            'pytorch': torch_numpy_random,
            'torchvision': torch_numpy_random,
            'keras': tf_numpy_random,
            'nltk': numpy_random,
            'spacy': numpy_random,
            'scrapy': set([])
        }
    def control_initialization_entropy(self, root_script_path, root_dir=None):
        """
        Client code only.
        Controls initialization entropy

        :param root_script_path: The path to the file that python was called on `python script.py`
        :return:
        """
        root_script_path = os.path.abspath(root_script_path)
        if root_dir is None:
            root_dir = os.path.dirname(root_script_path)
        watched_imports = set([])
        for path, contents in self._walk_tree(root_dir):
            watched_imports |= self._get_imports(contents)

        entropy_dependencies = set([])
        for imprt in watched_imports:
            entropy_dependencies |= self.entropy_dependencies[imprt]

        # DEBUG
        return entropy_dependencies
        # TODO: CONTINUE HERE

        statements = []
        if 'random' in entropy_dependencies:
            statements.extend(self._control_random_initialization())
        if 'numpy' in entropy_dependencies:
            statements.extend(self._control_numpy_initialization())
        if 'tensorflow' in entropy_dependencies:
            statements.extend(self._control_tf_initialization())
        if 'torch' in entropy_dependencies:
            statements.extend(self._control_torch_initialization())

        root_script_ast = self._transform_root_script(root_script_path, self._sort_control_statements(statements))

        self._write_ast(root_script_path, root_script_path)

    def _walk_tree(self, root_dir, filter=lambda abs_path: True):
        for (src_root, dirs, files) in os.walk(root_dir):
            for file in files:
                _, ext = os.path.splitext(file)
                abs_path = os.path.join(src_root, file)
                if ext == '.py' and filter(abs_path):
                    f = open(abs_path, 'r')
                    buff = f.read()
                    f.close()
                    yield abs_path, buff

    def _get_imports(self, contents):
        watched_imports = set([])
        astree = ast.parse(contents)

        def get_watched_import(node):
            nonlocal watched_imports
            if isinstance(node, ast.ImportFrom):
                name = node.module.split('.')[0]
                if name in self.entropy_dependencies:
                    watched_imports |= {name,}
            elif isinstance(node, ast.Import):
                for each in node.names:
                    get_watched_import(each)
            elif isinstance(node, ast.alias):
                name = node.name.split('.')[0]
                if name in self.entropy_dependencies:
                    watched_imports |= {name,}

        [get_watched_import(node) for node in astree.body]

        return watched_imports

    def _control_random_initialization(self):
        """

        :return: list of statements
        """
        pass

    def _control_numpy_initialization(self):
        """

        :return: list of statements
        """
        pass

    def _control_tf_initialization(self):
        """

        :return: list of statements
        """
        pass

    def _control_torch_initialization(self):
        """

        :return: list of statements
        """
        pass

    def _transform_root_script(self, root_script_path, statements):
        pass

    def _write_ast(self, ast, path):
        source_code = astor.to_source(ast)
        try:
            os.unlink(path)
        except:
            pass
        with open(path, 'w') as f:
            f.write('#flor_transformed' + '\n')
            f.write(source_code)

    def _sort_control_statements(self, statements):
        pass




