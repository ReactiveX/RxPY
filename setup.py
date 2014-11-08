import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system.
sys.path.pop(0)
from setuptools import setup

setup(name='micropython-rx',
    version='0.11.1',
    description='ReactiveX for MicroPython',
    long_description='is a library for composing asynchronous and event-based programs using observable collections and LINQ-style query operators in Python',
    url='https://github.com/reactivex/rxpy',
    author='Dag Brattli',
    author_email='dag@brattli.net',
    maintainer='Dag Brattli',
    maintainer_email='dag@brattli.net',
    license='Apache License',
    
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # 'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    #py_modules=['rx'],
    packages=['rx', 'rx.internal',
              'rx.linq', 'rx.linq.observable', 'rx.linq.enumerable',
              'rx.concurrency',
              'rx.disposables', 'rx.subjects', 'rx.testing'],
    package_dir = { 'rx':'rx' }
)
