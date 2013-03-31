from rx import Observable, AnonymousObservable

def default_comparer(x, y):
    if not y.equals:
        return x == y
    
    return x.equals(y)

def create_message(actual, expected):
    return 'Expected: [%s]\r\nActual: [%s]' % (str(expected), str(actual))

def are_elements_equal(expected, actual, comparer=None, message=None):
    is_ok = True
    comparer = comparer or default_comparer
    if len(expected) != len(actual):
        assert False, 'Not equal length. Expected: %s Actual: %s' % (len(expected), len(actual))
        return
    
    for i, ex in enumerate(expected):
        is_ok = comparer(ex, actual[i])
        if not is_ok:
            break
        
    assert is_ok, message or create_message(expected, actual)

def assert_equal(expected, *actual):
    actual = list(actual)
    return are_elements_equal(expected, actual, default_comparer)

class AssertList(list):
    def assert_equal(self, *actual):
        actual = list(actual)
        return are_elements_equal(self, actual, default_comparer)

class ObservableTest(object):
    # Observable.dump extension method
    def dump(self, name = "test"):
        def subscribe(observer):
            def on_next(value):
                print("{%s}-->{%s}" % (name, value))
                observer.on_next(value)
            def on_error(ex):
                print("{%s} error -->{%s}" % (name, ex))
                observer.on_error(ex)
            def on_completed():
                print("{%s} completed" % name)
                observer.on_completed()

            return self.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)

Observable.dump = ObservableTest.dump