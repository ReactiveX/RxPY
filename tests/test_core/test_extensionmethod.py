import unittest

from rx.internal import extensionmethod, extensionclassmethod

class A(object):
    def method_a(self, arg):
        return (self, arg)

@extensionmethod(A)
def method_b(self, *args):
    assert(len(args) == 1)
    return (self, args[0])

@extensionclassmethod(A)
def method_c(cls, *args):
    assert(len(args) == 1)
    return (cls, args[0])

@extensionmethod(A, decorator=staticmethod)
def method_s(*args):
    print("args: ", args)
    return args[0]

class TestExtensionMethod(unittest.TestCase):

    def test_method_a(self):
        a = A()
        assert(a.method_a(42) == (a, 42))

    def test_method_b(self):
        a = A()
        assert(a.method_b(42) == (a, 42))

    def test_classmethod(self):
        # We could wish for cls to be A, but this works for us
        a = A()
        assert(a.method_c(42) == (A, 42))

    def test_staticmethod(self):
        a = A()
        assert(a.method_s(42) == 42)

if __name__ == '__main__':
    unittest.main()
