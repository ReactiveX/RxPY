#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from configparser import ConfigParser


# General project metadata is stored in project.cfg
with open('project.cfg') as project_file:
    config = ConfigParser()
    config.read_file(project_file)
    project_meta = dict(config.items('project'))


# Populate the long_description field from README.rst
with open('README.rst') as readme_file:
    project_meta['long_description'] = readme_file.read()


setup(
    **{key: project_meta[key] for key in (
        'name',
        'version',
        'description',
        'long_description',
        'author',
        'author_email',
        'license',
        'url',
        'download_url'
    )},
    zip_safe=True,
    python_requires='>=3.6.0',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=4.6.1', 'pytest-asyncio>=0.10.0', 'coverage>=4.5.3'],

    package_data={'rx': ['py.typed']},
    packages=['rx', 'rx.internal', 'rx.core', 'rx.core.abc',
              'rx.core.operators', 'rx.core.operators.connectable',
              'rx.core.observable', 'rx.core.observer',
              'rx.scheduler', 'rx.scheduler.eventloop', 'rx.scheduler.mainloop',
              'rx.operators', 'rx.disposable', 'rx.subject',
              'rx.testing'],
    package_dir={'rx': 'rx'},
    include_package_data=True
)
