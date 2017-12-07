from rx.core import Observer
from rx.testing import TestScheduler, ReactiveTest
from rx.core.notification import OnNext, OnError, OnCompleted

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def test_send_ctor_and_props():
    n = OnNext(42)
    assert('N' == n.kind)
    assert(n.has_value)
    assert(42 == n.value)
    assert(not hasattr(n, "exception"))


def test_send_equality():
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


def test_send_tostring():
    n1 = OnNext(42)
    assert("OnNext" in str(n1))
    assert("42" in str(n1))


class CheckOnNextObserver(Observer):
    def __init__(self):
        super(CheckOnNextObserver, self).__init__()

        self.value = None

    def send(self, value):
        self.value = value
        return self.value

    def throw(self):
        raise NotImplementedError

    def close(self):
        def func():
            raise NotImplementedError
        return func


def test_send_accept_observer():
    con = CheckOnNextObserver()
    n1 = OnNext(42)
    n1.accept(con)
    assert(42 == con.value)


class AcceptObserver(Observer):
    def __init__(self, send, throw, close):
        self._send = send
        self._throw = throw
        self._close = close

    def send(self, value):
        return self._send(value)

    def throw(self, exception):
        return self._throw(exception)

    def close(self):
        return self._close()


def test_send_accept_observer_with_result():
    n1 = OnNext(42)

    def send(x):
        return "OK"
    def throw(err):
        assert(False)
    def close():
        assert(False)

    res = n1.accept(AcceptObserver(send, throw, close))
    assert('OK' == res)


def test_send_accept_action():
    obs = [False]
    n1 = OnNext(42)
    def send(x):
        obs[0] = True
        return obs[0]
    def throw(err):
        assert(False)
    def close():
        assert(False)
    n1.accept(send, throw, close)

    assert(obs[0])


def test_send_accept_action_with_result():
    n1 = OnNext(42)

    def send(x):
        return "OK"
    def throw(err):
        assert(False)
    def close():
        assert(False)

    res = n1.accept(send, throw, close)
    assert('OK' == res)


def test_throw_ctor_and_props():
    e = 'e'
    n = OnError(e)
    assert('E'== n.kind)
    assert(not n.has_value)
    assert(e == n.exception)


def test_throw_equality():
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


def test_throw_tostring():
    ex = 'ex'
    n1 = OnError(ex)
    assert("OnError" in str(n1))
    assert("ex" in str(n1))


class CheckOnErrorObserver(Observer):
    def __init__(self):
        super(CheckOnErrorObserver, self).__init__()

        self.error = None

    def send(value):
        raise NotImplementedError()

    def throw(self, exception):
        self.error = exception

    def close(self):
        raise NotImplementedError()


def test_throw_accept_observer():
    ex = 'ex'
    obs = CheckOnErrorObserver()
    n1 = OnError(ex)
    n1.accept(obs)
    assert(ex == obs.error)


def test_throw_accept_observer_with_result():
    ex = 'ex'
    n1 = OnError(ex)

    def send(x):
        assert(False)
        return None
    def throw(ex):
        return "OK"

    def close():
        assert(False)
        return None

    res = n1.accept(AcceptObserver(send, throw, close))
    assert('OK' == res)


def test_throw_accept_action():
    ex = 'ex'
    obs = [False]
    n1 = OnError(ex)

    def send(x):
        assert(False)
        return None
    def throw(ex):
        obs[0] = True
        return obs[0]
    def close():
        assert(False)
        return None

    n1.accept(send, throw, close)
    assert(obs[0])


def test_throw_accept_action_with_result():
    ex = 'ex'
    n1 = OnError(ex)

    def send(x):
        assert(False)
        return None
    def throw(ex):
        return "OK"
    def close():
        assert(False)
        return None

    res = n1.accept(send, throw, close)
    assert('OK' == res)


def test_close_ctor_and_props():
    n = OnCompleted()
    assert('C' == n.kind)
    assert(not n.has_value)
    assert(not hasattr(n, "exception"))


def test_close_equality():
    n1 = OnCompleted()
    n2 = OnCompleted()
    n3 = OnNext(2)
    assert(n1.equals(n1))
    assert(n1.equals(n2))
    assert(n2.equals(n1))
    assert(not n1.equals(None))
    assert(not n1.equals(n3))
    assert(not n3.equals(n1))


def test_close_tostring():
    n1 = OnCompleted()
    assert('OnCompleted' in str(n1))


class CheckOnCompletedObserver(Observer):
    def __init__(self):
        super(CheckOnCompletedObserver, self).__init__()

        self.completed = False

    def send(self):
        raise NotImplementedError()

    def throw(self):
        raise NotImplementedError()

    def close(self):
        self.completed = True


def test_close_accept_observer():
    obs = CheckOnCompletedObserver()
    n1 = OnCompleted()
    n1.accept(obs)
    assert(obs.completed)


def test_close_accept_observer_with_result():
    n1 = OnCompleted()

    def send(x):
        assert(False)
        return None
    def throw(err):
        assert(False)
        return None
    def close():
        return "OK"

    res = n1.accept(AcceptObserver(send, throw, close))
    assert('OK' == res)


def test_close_accept_action():
    obs = [False]
    n1 = OnCompleted()

    def send(x):
        assert(False)
        return None
    def throw(ex):
        assert(False)
        return None
    def close():
        obs[0] = True
        return obs[0]

    n1.accept(send, throw, close)
    assert(obs[0])


def test_close_accept_action_with_result():
    n1 = OnCompleted()

    def send(x):
        assert(False)
        return None
    def throw(ex):
        assert(False)
        return None
    def close():
        return "OK"

    res = n1.accept(send, throw, close)
    assert('OK' == res)


def test_to_observable_empty():
    scheduler = TestScheduler()

    def create():
        return OnCompleted().to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.close(201))


def test_to_observable_return():
    scheduler = TestScheduler()

    def create():
        return OnNext(42).to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.send(201, 42), ReactiveTest.close(201))


def test_to_observable_throw():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return OnError(ex).to_observable(scheduler)

    res = scheduler.start(create)
    res.messages.assert_equal(ReactiveTest.throw(201, ex))
