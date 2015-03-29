import unittest

from rx.internal.utils import adapt_call

class C(object):
    def __init__(self, arg):
        self._arg = arg

    def __call__(self, x):
        return x + self._arg
    
    def method1(self, x):
        return x + self._arg
    
    def method2(self, x, y):
        return x + self._arg
    
    def method3(self, x, y, z):
        return x + y + z + self._arg
    
    @classmethod
    def clsmethod(cls, x):
        return x * 10

    @staticmethod
    def stcmethod1(x):
        return x * 100


class TestUtil(unittest.TestCase):
    def test_adapt_call_method1(self):
        func = adapt_call(C(42).method1)
        value = func(2, 4)
        assert value == 44

    def test_adapt_call_call_object(self):
        func = adapt_call(C(42))
        value = func(2)
        assert value == 44

    def test_adapt_call_stcmethod1(self):
        func = adapt_call(C(42).stcmethod1)
        value = func(42)
        assert value == 4200

        value = func(42, 43)
        assert value == 4200

        value = func(42, 43, 44)
        assert value == 4200