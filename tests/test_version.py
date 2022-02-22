import unittest

from rx import __version__


class VersionTest(unittest.TestCase):
    def test_version(self):
        assert __version__
