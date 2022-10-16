from setuptools import setup

NAME = "xl"

DESCRIPTION = 'A Python module to process XML'


URL = 'https://github.com/meng89/' + NAME

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(name=NAME,
      version="0.1.0",
      description=DESCRIPTION,
      include_package_data=True,
      author='Chen Meng',
      author_email='ObserverChan@gmail.com',
      license='MIT',
      url=URL,
      py_modules=[NAME],
      classifiers=CLASSIFIERS)
