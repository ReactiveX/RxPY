import unittest

from reactivex import __version__


class VersionTest(unittest.TestCase):
    def test_version(self):
        assert __version__
