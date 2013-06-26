try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='Rx',
    version='0.1.1',
    description='Reactive Extensions for Python',
    long_description = """\
is a set of libraries to compose asynchronous and event-based programs using observable collections and LINQ-style query operators in Python 3""",
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='Apache License',
    url='https://github.com/dbrattli/Rx',
    download_url = 'https://github.com/dbrattli/RxPY',
    zip_safe = True,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',

    packages=['rx', 'rx.internal', 'rx.linq', 'rx.testing', 'rx.concurrency', 'rx.disposables', 'rx.subjects' ],
    package_dir = { 'rx':'rx' }
)
