try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='Rx',
    version='0.9.2',
    description='Reactive Extensions for Python',
    long_description = """\
is a set of libraries to compose asynchronous and event-based programs using observable collections and LINQ-style query operators in Python""",
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='Apache License',
    url='https://github.com/dbrattli/Rx',
    download_url = 'https://github.com/dbrattli/RxPY',
    install_requires=[
        'six>=1.5'
    ],
    zip_safe = True,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # 'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',

    packages=['rx', 'rx.internal',
              'rx.linq', 'rx.linq.observable', 'rx.linq.enumerable',
              'rx.concurrency', 'rx.concurrency.mainloopscheduler',
              'rx.disposables', 'rx.subjects', 'rx.backpressure', 'rx.testing'],
    package_dir = { 'rx':'rx' }
)
