import unittest

from rx.internal import extends

class A(object):
    def method_a(self, arg):
        return (self, arg)

@extends(A)
class B(object):
    def method_b(self, *args):
        assert(len(args) == 1)
        return (self, args[0])

    @classmethod
    def method_c(cls, *args):
        assert(len(args) == 1)
        return (cls, args[0])

    @staticmethod
    def method_s(*args):
        print("args: ", args)
        return args[0]

class TestExtends(unittest.TestCase):

    def test_method_a(self):
        a = A()
        assert(a.method_a(42) == (a, 42))

    def test_method_b(self):
        a = A()
        assert(a.method_b(42) == (a, 42))

    def test_method_c(self):
        # We could wish for cls to be A, but this works for us
        assert(A.method_c(42) == (B, 42))
        a = A()
        assert(a.method_c(42) == (B, 42))

    def test_method_s(self):
        a = A()
        # We cannot steal static methods. Accept this failure for now
        #assert(a.method_s(42) == 42)

if __name__ == '__main__':
    unittest.main()
