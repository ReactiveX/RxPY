#!/usr/bin/python
#
# Copyright (C) 2013 Dag Brattli.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from distutils.cmd import Command
from distutils.command.build_ext import build_ext
try:
    from setuptools import setup, Extension, Feature
except ImportError:
    from distutils.core import setup, Extension
    Feature = None
import sys

setup(
    name='RxPY',
    version='0.0.1',
    description='Reactive Extensions for Python',
    long_description = """\
Longer description for Reactive Extensions for Python.
""",
    author='Dag Brattli',
    author_email='dag@brattli.net',
    license='New BSD License',
    url='https://github.com/dbrattli/RxPy',
    download_url = 'https://github.com/dbrattli/RxPy',
    zip_safe = True,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
	    'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    test_suite='nose.collector',

    packages=['rx', 'linq', 'tests'],
    package_dir = { 'rx':'rx', 'linq' : 'linq', 'tests' : 'tests'}
)
