import unittest

from configparser import ConfigParser
from os.path import abspath, dirname, join
from re import match


class VersionTest(unittest.TestCase):

    def test_version(self):

        root = abspath(join(dirname(__file__), '..'))

        with open(join(root, 'project.cfg')) as project_file:
            config = ConfigParser()
            config.read_file(project_file)
            project_meta = dict(config.items('project'))

        version = None
        with open(join(root, 'rx', '__init__.py')) as init_py:
            for line in init_py:
                version = match('\\s*__version__\\s*=\\s*[\'"](.*)[\'"]', line)
                if version is not None:
                    version = version.group(1)
                    break

        assert project_meta['version'] == version
