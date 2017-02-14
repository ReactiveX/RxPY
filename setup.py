try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='Rx',
    version='1.5.8',
    description='Reactive Extensions (Rx) for Python',
    long_description=("is a library for composing asynchronous and "
        "event-based programs using observable collections and LINQ-style "
        "query operators in Python."),
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='Apache License',
    url='http://reactivex.io',
    download_url='https://github.com/ReactiveX/RxPY',
    zip_safe=True,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: IronPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',

    packages=['rx', 'rx.core', 'rx.core.py2', 'rx.core.py3', 'rx.internal',
              'rx.linq', 'rx.linq.observable', 'rx.linq.enumerable',
              'rx.concurrency', 'rx.concurrency.mainloopscheduler', 'rx.joins',
              'rx.linq.observable.blocking', 'rx.disposables', 'rx.subjects',
              'rx.backpressure', 'rx.testing'],
    package_dir={'rx': 'rx'}
)
