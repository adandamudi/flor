import setuptools
import io

with io.open("README.md", mode="r", encoding='utf-8') as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as f:
    requirements = f.read().split('\n')

setuptools.setup(
     name='pyflor',
     version='1.0.0',
     author="Rolando Garcia",
     author_email="rogarcia@berkeley.edu",
     description="Fast Low-Overhead Recovery suite",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/ucbrise/flor",
     packages=['flor',
               'flor.logger',
               'flor.transformer',
               'flor.skipblock'],
     install_requires = requirements,
     classifiers = [
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
     ]
 )
