try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='RxPY',
    version='0.0.1',
    description='Reactive Extensions for Python',
    long_description = """\
Longer description for Reactive Extensions for Python.
""",
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='Apache License',
    url='https://github.com/dbrattli/RxPy',
    download_url = 'https://github.com/dbrattli/RxPy',
    zip_safe = True,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',

    packages=['rx', 'linq', 'tests'],
    package_dir = { 'rx':'rx', 'linq' : 'linq' }#, 'tests' : 'tests'}
)
