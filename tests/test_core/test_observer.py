from typing import Any

from reactivex import Observer
from reactivex.notification import (
    Notification,
    OnCompleted,
    OnError,
    OnNext,
    from_notifier,
)


class MyObserver(Observer[Any]):
    def __init__(self) -> None:
        super().__init__()
        self.has_on_next: Any = None
        self.has_on_completed: bool | None = None
        self.has_on_error: str | None = None

    def _on_next_core(self, value: Any) -> None:
        self.has_on_next = value

    def _on_error_core(self, error: Exception) -> None:
        self.has_on_error = str(error)

    def _on_completed_core(self) -> None:
        self.has_on_completed = True


def test_to_observer_notification_on_next() -> None:
    i = 0

    def next(n: Notification[int]) -> None:
        assert i == 0
        assert n.kind == "N"
        assert isinstance(n, OnNext)
        assert n.value == 42
        assert not hasattr(n, "exception")
        assert n.has_value

    from_notifier(next).on_next(42)


def test_to_observer_notification_on_error() -> None:
    ex = Exception("ex")
    i = 0

    def next(n: Notification[Any]) -> None:
        assert i == 0
        assert n.kind == "E"
        assert isinstance(n, OnError)
        assert str(n.exception) == "ex"
        assert not n.has_value

    from_notifier(next).on_error(ex)


def test_to_observer_notification_completed() -> None:
    i = 0

    def next(n: Notification[Any]) -> None:
        assert i == 0
        assert n.kind == "C"
        assert isinstance(n, OnCompleted)
        assert not n.has_value

    from_notifier(next).on_completed()


def test_to_notifier_forwards() -> None:
    obsn = MyObserver()
    obsn.to_notifier()(OnNext(42))
    assert obsn.has_on_next == 42

    ex = Exception("ex")
    obse = MyObserver()
    obse.to_notifier()(OnError(ex))
    assert "ex" == obse.has_on_error

    obsc = MyObserver()
    obsc.to_notifier()(OnCompleted())
    assert obsc.has_on_completed


def test_create_on_next() -> None:
    next = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    res = Observer(on_next)

    res.on_next(42)
    assert next[0]
    res.on_completed()


def test_create_on_next_has_error() -> None:
    ex = Exception("ex")
    next = [False]
    e_: Exception | None = None

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    res: Observer[int] = Observer(on_next)

    res.on_next(42)
    assert next[0]

    try:
        res.on_error(ex)
        assert False
    except Exception as e:
        e_ = e

    assert str(ex) in str(e_)


def test_create_on_next_on_completed() -> None:
    next = [False]
    completed = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_completed() -> None:
        completed[0] = True

    res: Observer[int] = Observer(on_next, None, on_completed)

    res.on_next(42)

    assert next[0]
    assert not completed[0]

    res.on_completed()

    assert completed[0]


def test_create_on_next_close_has_error() -> None:
    e_: Exception | None = None
    ex = Exception("ex")
    next = [False]
    completed = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_completed() -> None:
        completed[0] = True

    res: Observer[int] = Observer(on_next, None, on_completed)

    res.on_next(42)
    assert next[0]
    assert not completed[0]
    try:
        res.on_error(ex)
        assert False
    except Exception as e:
        e_ = e

    assert str(ex) in str(e_)
    assert not completed[0]


def test_create_on_next_on_error() -> None:
    ex = Exception("ex")
    next = [True]
    error = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_error(e: Exception) -> None:
        assert ex == e
        error[0] = True

    res: Observer[int] = Observer(on_next, on_error)

    res.on_next(42)

    assert next[0]
    assert not error[0]

    res.on_error(ex)
    assert error[0]


def test_create_on_next_throw_hit_completed() -> None:
    ex = Exception("ex")
    next = [True]
    error = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_error(e: Exception) -> None:
        assert ex == e
        error[0] = True

    res: Observer[int] = Observer(on_next, on_error)

    res.on_next(42)
    assert next[0]
    assert not error[0]

    res.on_completed()

    assert not error[0]


def test_create_on_next_throw_close1() -> None:
    ex = Exception("ex")
    next = [True]
    error = [False]
    completed = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_error(e: Exception) -> None:
        assert ex == e
        error[0] = True

    def on_completed() -> None:
        completed[0] = True

    res: Observer[int] = Observer(on_next, on_error, on_completed)

    res.on_next(42)

    assert next[0]
    assert not error[0]
    assert not completed[0]

    res.on_completed()

    assert completed[0]
    assert not error[0]


def test_create_on_next_throw_close2() -> None:
    ex = Exception("ex")
    next = [True]
    error = [False]
    completed = [False]

    def on_next(x: int) -> None:
        assert 42 == x
        next[0] = True

    def on_error(e: Exception) -> None:
        assert ex == e
        error[0] = True

    def on_completed() -> None:
        completed[0] = True

    res: Observer[int] = Observer(on_next, on_error, on_completed)

    res.on_next(42)

    assert next[0]
    assert not error[0]
    assert not completed[0]

    res.on_error(ex)

    assert not completed[0]
    assert error[0]


def test_as_observer_hides() -> None:
    obs = MyObserver()
    res = obs.as_observer()

    assert res != obs
    assert not isinstance(res, obs.__class__)


def test_as_observer_forwards() -> None:
    obsn = MyObserver()
    obsn.as_observer().on_next(42)
    assert obsn.has_on_next == 42

    ex = Exception("ex")
    obse = MyObserver()
    obse.as_observer().on_error(ex)
    assert obse.has_on_error == "ex"

    obsc = MyObserver()
    obsc.as_observer().on_completed()
    assert obsc.has_on_completed


if __name__ == "__main__":
    test_to_notifier_forwards()
