from nose.tools import assert_raises

from rx.core import ObserverBase, AnonymousObserver
from rx.core.notification import OnNext, OnError, OnCompleted, from_notifier
from rx.internal.exceptions import CompletedException


class MyObserver(ObserverBase):
    def __init__(self):
        super().__init__()
        self.has_send = None
        self.has_close = None
        self.has_throw = None

    def _send_core(self, value):
        self.has_send = value

    def _throw_core(self, error):
        self.has_throw = error

    def _close_core(self):
        self.has_close = True


def test_to_observer_notification_send():
    i = 0

    def next(n):
        assert(i == 0)
        assert(n.kind == 'N')
        assert(n.value == 42)
        assert(not hasattr(n, "exception"))
        assert(n.has_value)

    from_notifier(next).send(42)


def test_to_observer_notification_throw():
    ex = 'ex'
    i = 0

    def next(n):
        assert(i == 0)
        assert(n.kind == 'E')
        assert(n.exception == ex)
        assert(not n.has_value)

    from_notifier(next).throw(ex)


def test_to_observer_notification_close():
    i = 0

    def next(n):
        assert(i == 0)
        assert(n.kind == 'C')
        assert(not n.has_value)

    from_notifier(next).close()


def test_to_notifier_forwards():
    obsn = MyObserver()
    obsn.to_notifier()(OnNext(42))
    assert(obsn.has_send == 42)

    ex = 'ex'
    obse = MyObserver()
    obse.to_notifier()(OnError(ex))
    assert(ex == obse.has_throw)

    obsc = MyObserver()
    obsc.to_notifier()(OnCompleted())
    assert(obsc.has_close)


def test_create_send():
    next = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    res = AnonymousObserver(send)

    res.send(42)
    assert(next[0])
    return res.close()


def test_create_send_has_error():
    ex = 'ex'
    next = [False]
    _e = None

    def send(x):
        assert(42 == x)
        next[0] = True

    res = AnonymousObserver(send)

    res.send(42)
    assert(next[0])

    try:
        res.throw(ex)
        assert(False)
    except Exception as e:
        e_ = e.args[0]

    assert(ex == e_)


def test_create_send_close():
    next = [False]
    completed = [False]

    def send(x):
        assert(42 == x)
        next[0] = True
        return next[0]

    def close():
        completed[0] = True
        return completed[0]

    res = AnonymousObserver(send, None, close)

    res.send(42)

    assert(next[0])
    assert(not completed[0])

    res.close()

    assert(completed[0])


def test_create_send_close_has_error():
    e_ = None
    ex = 'ex'
    next = [False]
    completed = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    def close():
        completed[0] = True

    res = AnonymousObserver(send, None, close)

    res.send(42)
    assert(next[0])
    assert(not completed[0])
    try:
        res.throw(ex)
        assert(False)
    except Exception as e:
        e_ = e.args[0]

    assert(ex == e_)
    assert(not completed[0])


def test_create_send_throw():
    ex = 'ex'
    next = [True]
    error = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    def throw(e):
        assert(ex == e)
        error[0] = True

    res = AnonymousObserver(send, throw)

    res.send(42)

    assert(next[0])
    assert(not error[0])

    res.throw(ex)
    assert(error[0])


def test_create_send_throw_hit_completed():
    ex = 'ex'
    next = [True]
    error = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    def throw(e):
        assert(ex == e)
        error[0] = True

    res = AnonymousObserver(send, throw)

    res.send(42)
    assert(next[0])
    assert(not error[0])

    res.close()

    assert(not error[0])


def test_create_send_throw_close1():
    ex = 'ex'
    next = [True]
    error = [False]
    completed = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    def throw(e):
        assert(ex == e)
        error[0] = True

    def close():
        completed[0] = True

    res = AnonymousObserver(send, throw, close)

    res.send(42)

    assert(next[0])
    assert(not error[0])
    assert(not completed[0])

    res.close()

    assert(completed[0])
    assert(not error[0])


def test_create_send_throw_close2():
    ex = 'ex'
    next = [True]
    error = [False]
    completed = [False]

    def send(x):
        assert(42 == x)
        next[0] = True

    def throw(e):
        assert(ex == e)
        error[0] = True

    def close():
        completed[0] = True

    res = AnonymousObserver(send, throw, close)

    res.send(42)

    assert(next[0])
    assert(not error[0])
    assert(not completed[0])

    res.throw(ex)

    assert(not completed[0])
    assert(error[0])


def test_as_observer_hides():
    obs = MyObserver()
    res = obs.as_observer()

    assert(res != obs)
    assert(not isinstance(res, obs.__class__))
    assert(not isinstance(obs, res.__class__))


def test_as_observer_forwards():
    obsn = MyObserver()
    obsn.as_observer().send(42)
    assert(obsn.has_send == 42)

    ex = 'ex'
    obse = MyObserver()
    obse.as_observer().throw(ex)
    assert(obse.has_throw == ex)

    obsc = MyObserver()
    obsc.as_observer().close()
    assert(obsc.has_close)


def test_observer_checked_already_terminated_completed():
    m, n = [0], [0]

    def send(x):
        m[0] += 1

    def throw(x):
        assert(False)

    def close():
        n[0] += 1

    o = AnonymousObserver(send, throw, close).checked()

    o.send(1)
    o.send(2)
    o.close()

    assert_raises(CompletedException, o.close)

    try:
        o.throw(Exception('error'))
    except Exception:
        pass

    assert(2 == m[0])
    assert(1 == n[0])


def test_observer_checked_already_terminated_error():
    m, n = [0], [0]

    def send(x):
        m[0] += 1

    def throw(x):
        n[0] += 1

    def close():
        assert(False)

    o = AnonymousObserver(send, throw, close).checked()

    o.send(1)
    o.send(2)
    o.throw(Exception('error'))

    try:
        o.close()
    except Exception:
        pass

    try:
        o.throw(Exception('error'))
    except Exception:
        pass

    assert(2 == m[0])
    assert(1 == n[0])


def test_observer_checked_reentrant_next():
    ex = "Re-entrancy detected"
    n = [0]

    def send(x):
        n[0] += 1

        try:
            o.send(9)
        except Exception as e:
            assert str(e) == ex

        try:
            o.throw(Exception('error'))
        except Exception as e:
            assert str(e) == ex

        try:
            o.close()
        except Exception as e:
            assert str(e) == ex

    def throw(ex):
        assert(False)

    def close():
        assert(False)
    o = AnonymousObserver(send, throw, close).checked()

    o.send(1)
    assert(1 == n[0])


def test_observer_checked_reentrant_error():
    msg = "Re-entrancy detected"
    n = [0]

    def send(x):
        assert(False)

    def throw(ex):
        n[0] += 1

        try:
            o.send(9)
        except Exception as e:
            assert str(e) == msg

        try:
            o.throw(Exception('error'))
        except Exception as e:
            assert str(e) == msg

        try:
            o.close()
        except Exception as e:
            assert str(e) == msg

    def close():
        assert(False)

    o = AnonymousObserver(send, throw, close).checked()
    o.throw(Exception('error'))
    assert(1 == n[0])


def test_observer_checked_reentrant_completed():
    msg = "Re-entrancy detected"
    n = [0]

    def send(x):
        assert(False)

    def throw(ex):
        assert(False)

    def close():
        n[0] += 1
        try:
            o.send(9)
        except Exception as e:
            print(str(e))
            assert str(e) == msg

        try:
            o.throw(Exception('error'))
        except Exception as e:
            assert str(e) == msg

        try:
            o.close()
        except Exception as e:
            assert str(e) == msg

    o = AnonymousObserver(send, throw, close).checked()

    o.close()
    assert(1 == n[0])

if __name__ == '__main__':
    test_to_notifier_forwards()
