try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='Rx',
    version='3.0.0-alpha',
    description='Reactive Extensions (Rx) for Python',
    long_description=(
        "is a library for composing asynchronous and "
        "event-based programs using observable collections and LINQ-style "
        "query operators in Python."),
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='Apache License',
    url='http://reactivex.io',
    download_url='https://github.com/ReactiveX/RxPY',
    zip_safe=True,
    python_requires='>=3.5.0',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', "pytest-asyncio"],

    packages=['rx', 'rx.internal', 'rx.core', 'rx.core.abc',
              'rx.core.operators', 'rx.core.observable', 'rx.core.observer',
              'rx.core.operators.blocking', 'rx.core.operators.connectable',
              'rx.concurrency', 'rx.concurrency.mainloopscheduler',
              'rx.operators', 'rx.disposables', 'rx.subjects',
              'rx.testing'],
    package_dir={'rx': 'rx'},
    include_package_data=True,
)
