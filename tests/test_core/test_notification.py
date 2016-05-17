from rx.core import Observer
from rx.testing import TestScheduler, ReactiveTest
from rx.core.notification import OnNext, OnError, OnCompleted

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def test_on_next_ctor_and_props():
    n = OnNext(42)
    assert('N' == n.kind)
    assert(n.has_value)
    assert(42 == n.value)
    assert(not hasattr(n, "exception"))


def test_on_next_equality():
    n1 = OnNext(42)
    n2 = OnNext(42)
    n3 = OnNext(24)
    n4 = OnCompleted()
    assert(n1.equals(n1))
    assert(n1.equals(n2))
    assert(n2.equals(n1))
    assert(not n1.equals(None))
    assert(not n1.equals(n3))
    assert(not n3.equals(n1))
    assert(not n1.equals(n4))
    assert(not n4.equals(n1))


def test_on_next_tostring():
    n1 = OnNext(42)
    assert("OnNext" in str(n1))
    assert("42" in str(n1))


class CheckOnNextObserver(Observer):
    def __init__(self):
        super(CheckOnNextObserver, self).__init__()

        self.value = None

    def on_next(self, value):
        self.value = value
        return self.value

    def on_error(self):
        raise NotImplementedError

    def on_completed(self):
        def func():
            raise NotImplementedError
        return func


def test_on_next_accept_observer():
    con = CheckOnNextObserver()
    n1 = OnNext(42)
    n1.accept(con)
    assert(42 == con.value)


class AcceptObserver(Observer):
    def __init__(self, on_next, on_error, on_completed):
        self._on_next = on_next
        self._on_error = on_error
        self._on_completed = on_completed

    def on_next(self, value):
        return self._on_next(value)

    def on_error(self, exception):
        return self._on_error(exception)

    def on_completed(self):
        return self._on_completed()


def test_on_next_accept_observer_with_result():
    n1 = OnNext(42)

    def on_next(x):
        return "OK"
    def on_error(err):
        assert(False)
    def on_completed():
        assert(False)

    res = n1.accept(AcceptObserver(on_next, on_error, on_completed))
    assert('OK' == res)


def test_on_next_accept_action():
    obs = [False]
    n1 = OnNext(42)
    def on_next(x):
        obs[0] = True
        return obs[0]
    def on_error(err):
        assert(False)
    def on_completed():
        assert(False)
    n1.accept(on_next, on_error, on_completed)

    assert(obs[0])


def test_on_next_accept_action_with_result():
    n1 = OnNext(42)

    def on_next(x):
        return "OK"
    def on_error(err):
        assert(False)
    def on_completed():
        assert(False)

    res = n1.accept(on_next, on_error, on_completed)
    assert('OK' == res)


def test_on_error_ctor_and_props():
    e = 'e'
    n = OnError(e)
    assert('E'== n.kind)
    assert(not n.has_value)
    assert(e == n.exception)


def test_on_error_equality():
    ex1 = 'ex1'
    ex2 = 'ex2'
    n1 = OnError(ex1)
    n2 = OnError(ex1)
    n3 = OnError(ex2)
    n4 = OnCompleted()
    assert(n1.equals(n1))
    assert(n1.equals(n2))
    assert(n2.equals(n1))
    assert(not n1.equals(None))
    assert(not n1.equals(n3))
    assert(not n3.equals(n1))
    assert(not n1.equals(n4))
    assert(not n4.equals(n1))


def test_on_error_tostring():
    ex = 'ex'
    n1 = OnError(ex)
    assert("OnError" in str(n1))
    assert("ex" in str(n1))


class CheckOnErrorObserver(Observer):
    def __init__(self):
        super(CheckOnErrorObserver, self).__init__()

        self.error = None

    def on_next(value):
        raise NotImplementedError()

    def on_error(self, exception):
        self.error = exception

    def on_completed(self):
        raise NotImplementedError()


def test_on_error_accept_observer():
    ex = 'ex'
    obs = CheckOnErrorObserver()
    n1 = OnError(ex)
    n1.accept(obs)
    assert(ex == obs.error)


def test_on_error_accept_observer_with_result():
    ex = 'ex'
    n1 = OnError(ex)

    def on_next(x):
        assert(False)
        return None
    def on_error(ex):
        return "OK"

    def on_completed():
        assert(False)
        return None

    res = n1.accept(AcceptObserver(on_next, on_error, on_completed))
    assert('OK' == res)


def test_on_error_accept_action():
    ex = 'ex'
    obs = [False]
    n1 = OnError(ex)

    def on_next(x):
        assert(False)
        return None
    def on_error(ex):
        obs[0] = True
        return obs[0]
    def on_completed():
        assert(False)
        return None

    n1.accept(on_next, on_error, on_completed)
    assert(obs[0])


def test_on_error_accept_action_with_result():
    ex = 'ex'
    n1 = OnError(ex)

    def on_next(x):
        assert(False)
        return None
    def on_error(ex):
        return "OK"
    def on_completed():
        assert(False)
        return None

    res = n1.accept(on_next, on_error, on_completed)
    assert('OK' == res)


def test_on_completed_ctor_and_props():
    n = OnCompleted()
    assert('C' == n.kind)
    assert(not n.has_value)
    assert(not hasattr(n, "exception"))


def test_on_completed_equality():
    n1 = OnCompleted()
    n2 = OnCompleted()
    n3 = OnNext(2)
    assert(n1.equals(n1))
    assert(n1.equals(n2))
    assert(n2.equals(n1))
    assert(not n1.equals(None))
    assert(not n1.equals(n3))
    assert(not n3.equals(n1))


def test_on_completed_tostring():
    n1 = OnCompleted()
    assert('OnCompleted' in str(n1))


class CheckOnCompletedObserver(Observer):
    def __init__(self):
        super(CheckOnCompletedObserver, self).__init__()

        self.completed = False

    def on_next(self):
        raise NotImplementedError()

    def on_error(self):
        raise NotImplementedError()

    def on_completed(self):
        self.completed = True


def test_on_completed_accept_observer():
    obs = CheckOnCompletedObserver()
    n1 = OnCompleted()
    n1.accept(obs)
    assert(obs.completed)


def test_on_completed_accept_observer_with_result():
    n1 = OnCompleted()

    def on_next(x):
        assert(False)
        return None
    def on_error(err):
        assert(False)
        return None
    def on_completed():
        return "OK"

    res = n1.accept(AcceptObserver(on_next, on_error, on_completed))
    assert('OK' == res)


def test_on_completed_accept_action():
    obs = [False]
    n1 = OnCompleted()

    def on_next(x):
        assert(False)
        return None
    def on_error(ex):
        assert(False)
        return None
    def on_completed():
        obs[0] = True
        return obs[0]

    n1.accept(on_next, on_error, on_completed)
    assert(obs[0])


def test_on_completed_accept_action_with_result():
    n1 = OnCompleted()

    def on_next(x):
        assert(False)
        return None
    def on_error(ex):
        assert(False)
        return None
    def on_completed():
        return "OK"

    res = n1.accept(on_next, on_error, on_completed)
    assert('OK' == res)


def test_to_observable_empty():
    scheduler = TestScheduler()

    def create():
        return OnCompleted().to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.on_completed(201))


def test_to_observable_return():
    scheduler = TestScheduler()

    def create():
        return OnNext(42).to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.on_next(201, 42), ReactiveTest.on_completed(201))


def test_to_observable_throw():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return OnError(ex).to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.on_error(201, ex))
