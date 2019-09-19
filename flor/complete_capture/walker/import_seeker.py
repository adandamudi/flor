import os

class ImportSeeker():

    def __init__(self, rootpath):
        """
        :param rootpath: Absolute path we want to transform
        """

        self.rootpath = os.path.abspath(rootpath)

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

        # The libraries have the following transitive dependencies (need to capture those states)

        self.state_getters = {'numpy',
                              'scipy',
                              'pandas',
                              'statsmodels',
                              'matplotlib',
                              'seaborn',
                              'plotly',
                              'bokeh',
                              'pydot',
                              'sklearn',
                              'xgboost',
                              'lightgbm',
                              'eli5',
                              'tensorboard',
                              'tensorflow',
                              'tensorflow_estimator',
                              'torch',
                              'pytorch',
                              'torchvision',
                              'keras',
                              'nltk',
                              'spacy',
                              'scrapy'
        }