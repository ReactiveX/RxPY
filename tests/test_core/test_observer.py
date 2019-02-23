from rx.core import Observer
from rx.core.notification import OnNext, OnError, OnCompleted, from_notifier


class MyObserver(Observer):

    def __init__(self):
        super().__init__()
        self.has_on_next = None
        self.has_on_completed = None
        self.has_on_error = None

    def _on_next_core(self, value):
        self.has_on_next = value

    def _on_error_core(self, error):
        self.has_on_error = error

    def _on_completed_core(self):
        self.has_on_completed = True


def test_to_observer_notification_on_next():
    i = 0

    def next(n):
        assert i == 0
        assert n.kind == 'N'
        assert n.value == 42
        assert not hasattr(n, "exception")
        assert n.has_value

    from_notifier(next).on_next(42)


def test_to_observer_notification_on_error():
    ex = 'ex'
    i = 0

    def next(n):
        assert i == 0
        assert n.kind == 'E'
        assert n.exception == ex
        assert not n.has_value

    from_notifier(next).on_error(ex)


def test_to_observer_notification_completed():
    i = 0

    def next(n):
        assert i == 0
        assert n.kind == 'C'
        assert not n.has_value

    from_notifier(next).on_completed()


def test_to_notifier_forwards():
    obsn = MyObserver()
    obsn.to_notifier()(OnNext(42))
    assert obsn.has_on_next == 42

    ex = 'ex'
    obse = MyObserver()
    obse.to_notifier()(OnError(ex))
    assert ex == obse.has_on_error

    obsc = MyObserver()
    obsc.to_notifier()(OnCompleted())
    assert obsc.has_on_completed


def test_create_on_next():
    next = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    res = Observer(on_next)

    res.on_next(42)
    assert next[0]
    return res.on_completed()


def test_create_on_next_has_error():
    ex = 'ex'
    next = [False]
    _e = None

    def on_next(x):
        assert 42 == x
        next[0] = True

    res = Observer(on_next)

    res.on_next(42)
    assert next[0]

    try:
        res.on_error(ex)
        assert False
    except Exception as e:
        e_ = e.args[0]

    assert ex == e_


def test_create_on_next_on_completed():
    next = [False]
    completed = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True
        return next[0]

    def on_completed():
        completed[0] = True
        return completed[0]

    res = Observer(on_next, None, on_completed)

    res.on_next(42)

    assert next[0]
    assert not completed[0]

    res.on_completed()

    assert completed[0]


def test_create_on_next_close_has_error():
    e_ = None
    ex = 'ex'
    next = [False]
    completed = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    def on_completed():
        completed[0] = True

    res = Observer(on_next, None, on_completed)

    res.on_next(42)
    assert next[0]
    assert not completed[0]
    try:
        res.on_error(ex)
        assert False
    except Exception as e:
        e_ = e.args[0]

    assert ex == e_
    assert not completed[0]


def test_create_on_next_on_error():
    ex = 'ex'
    next = [True]
    error = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    def on_error(e):
        assert ex == e
        error[0] = True

    res = Observer(on_next, on_error)

    res.on_next(42)

    assert next[0]
    assert not error[0]

    res.on_error(ex)
    assert error[0]


def test_create_on_next_throw_hit_completed():
    ex = 'ex'
    next = [True]
    error = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    def on_error(e):
        assert ex == e
        error[0] = True

    res = Observer(on_next, on_error)

    res.on_next(42)
    assert next[0]
    assert not error[0]

    res.on_completed()

    assert not error[0]


def test_create_on_next_throw_close1():
    ex = 'ex'
    next = [True]
    error = [False]
    completed = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    def on_error(e):
        assert ex == e
        error[0] = True

    def on_completed():
        completed[0] = True

    res = Observer(on_next, on_error, on_completed)

    res.on_next(42)

    assert next[0]
    assert not error[0]
    assert not completed[0]

    res.on_completed()

    assert completed[0]
    assert not error[0]


def test_create_on_next_throw_close2():
    ex = 'ex'
    next = [True]
    error = [False]
    completed = [False]

    def on_next(x):
        assert 42 == x
        next[0] = True

    def on_error(e):
        assert ex == e
        error[0] = True

    def on_completed():
        completed[0] = True

    res = Observer(on_next, on_error, on_completed)

    res.on_next(42)

    assert next[0]
    assert not error[0]
    assert not completed[0]

    res.on_error(ex)

    assert not completed[0]
    assert error[0]


def test_as_observer_hides():
    obs = MyObserver()
    res = obs.as_observer()

    assert res != obs
    assert not isinstance(res, obs.__class__)


def test_as_observer_forwards():
    obsn = MyObserver()
    obsn.as_observer().on_next(42)
    assert obsn.has_on_next == 42

    ex = 'ex'
    obse = MyObserver()
    obse.as_observer().on_error(ex)
    assert obse.has_on_error == ex

    obsc = MyObserver()
    obsc.as_observer().on_completed()
    assert obsc.has_on_completed


if __name__ == '__main__':
    test_to_notifier_forwards()
