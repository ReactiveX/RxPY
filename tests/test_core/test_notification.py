from typing import Any, cast

from reactivex.abc import ObserverBase
from reactivex.notification import OnCompleted, OnError, OnNext
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def test_on_next_ctor_and_props() -> None:
    n = OnNext(42)
    assert "N" == n.kind
    assert n.has_value
    assert 42 == n.value
    assert not hasattr(n, "exception")


def test_on_next_equality() -> None:
    n1 = OnNext(42)
    n2 = OnNext(42)
    n3 = OnNext(24)
    n4: OnCompleted[int] = OnCompleted()
    assert n1.equals(n1)
    assert n1.equals(n2)
    assert n2.equals(n1)
    assert n1 is not None
    assert not n1.equals(n3)
    assert not n3.equals(n1)
    assert not n1.equals(n4)
    assert not n4.equals(n1)


def test_on_next_tostring() -> None:
    n1 = OnNext(42)
    assert "OnNext" in str(n1)
    assert "42" in str(n1)


class CheckOnNextObserver(ObserverBase[Any]):
    def __init__(self) -> None:
        super().__init__()

        self.value: Any = None

    def on_next(self, value: Any) -> None:
        self.value = value

    def on_error(self, error: Exception) -> None:
        raise NotImplementedError

    def on_completed(self) -> None:
        raise NotImplementedError


def test_on_next_accept_observer() -> None:
    con = CheckOnNextObserver()
    n1 = OnNext(42)
    n1.accept(con)
    assert con.value == 42


class AcceptObserver(ObserverBase[Any]):
    def __init__(
        self,
        on_next: Any,
        on_error: Any,
        on_completed: Any,
    ) -> None:
        self._on_next = on_next
        self._on_error = on_error
        self._on_completed = on_completed

    def on_next(self, value: Any) -> Any:
        return self._on_next(value)

    def on_error(self, error: Exception) -> Any:
        return self._on_error(error)

    def on_completed(self) -> Any:
        return self._on_completed()


def test_on_next_accept_observer_with_result() -> None:
    n1 = OnNext(42)

    def on_next(x: int) -> str:
        return "OK"

    def on_error(err: Exception) -> None:
        assert False

    def on_completed() -> None:
        assert False

    # Cast is safe: AcceptObserver intentionally returns values for testing
    res = cast(str, n1.accept(AcceptObserver(on_next, on_error, on_completed)))
    assert "OK" == res


def test_on_next_accept_action() -> None:
    obs = [False]
    n1 = OnNext(42)

    def on_next(x: int) -> None:
        obs[0] = True

    def on_error(err: Exception) -> None:
        assert False

    def on_completed() -> None:
        assert False

    n1.accept(on_next, on_error, on_completed)

    assert obs[0]


def test_on_next_accept_action_with_result() -> None:
    n1 = OnNext(42)

    def on_next(x: int) -> str:
        return "OK"

    def on_error(err: Exception) -> None:
        assert False

    def on_completed() -> None:
        assert False

    # Cast is safe: testing internal behavior where callbacks return values
    res = cast(str, n1.accept(cast(Any, on_next), on_error, on_completed))
    assert "OK" == res


def test_throw_ctor_and_props() -> None:
    e = Exception("e")
    n: OnError[int] = OnError(e)
    assert "E" == n.kind
    assert not n.has_value
    assert "e" == str(n.exception)


def test_throw_equality() -> None:
    ex1 = Exception("ex1")
    ex2 = Exception("ex2")
    n1: OnError[int] = OnError(ex1)
    n2: OnError[int] = OnError(ex1)
    n3: OnError[int] = OnError(ex2)
    n4: OnCompleted[int] = OnCompleted()
    assert n1.equals(n1)
    assert n1.equals(n2)
    assert n2.equals(n1)
    assert n1 is not None
    assert not n1.equals(n3)
    assert not n3.equals(n1)
    assert not n1.equals(n4)
    assert not n4.equals(n1)


def test_throw_tostring() -> None:
    ex = Exception("ex")
    n1: OnError[int] = OnError(ex)
    assert "OnError" in str(n1)
    assert "ex" in str(n1)


class CheckOnErrorObserver(ObserverBase[Any]):
    def __init__(self) -> None:
        super().__init__()

        self.error: str | None = None

    def on_next(self, value: Any) -> None:
        raise NotImplementedError()

    def on_error(self, error: Exception) -> None:
        self.error = str(error)

    def on_completed(self) -> None:
        raise NotImplementedError()


def test_throw_accept_observer() -> None:
    ex = Exception("ex")
    obs = CheckOnErrorObserver()
    n1: OnError[Any] = OnError(ex)
    n1.accept(obs)
    assert "ex" == obs.error


def test_throw_accept_observer_with_result() -> None:
    ex = Exception("ex")
    n1: OnError[Any] = OnError(ex)

    def on_next(x: Any) -> None:
        assert False

    def on_error(ex: Exception) -> str:
        return "OK"

    def on_completed() -> None:
        assert False

    # Cast is safe: AcceptObserver intentionally returns values for testing
    res = cast(str, n1.accept(AcceptObserver(on_next, on_error, on_completed)))
    assert "OK" == res


def test_throw_accept_action() -> None:
    ex = Exception("ex")
    obs = [False]
    n1: OnError[Any] = OnError(ex)

    def on_next(x: Any) -> None:
        assert False

    def on_error(ex: Exception) -> None:
        obs[0] = True

    def on_completed() -> None:
        assert False

    n1.accept(on_next, on_error, on_completed)
    assert obs[0]


def test_throw_accept_action_with_result() -> None:
    ex = Exception("ex")
    n1: OnError[Any] = OnError(ex)

    def on_next(x: Any) -> None:
        assert False

    def on_error(ex: Exception) -> str:
        return "OK"

    def on_completed() -> None:
        assert False

    # Cast is safe: testing internal behavior where callbacks return values
    res = cast(str, n1.accept(cast(Any, on_next), cast(Any, on_error), on_completed))
    assert "OK" == res


def test_close_ctor_and_props() -> None:
    n: OnCompleted[int] = OnCompleted()
    assert "C" == n.kind
    assert not n.has_value
    assert not hasattr(n, "exception")


def test_close_equality() -> None:
    n1: OnCompleted[int] = OnCompleted()
    n2: OnCompleted[int] = OnCompleted()
    n3 = OnNext(2)
    assert n1.equals(n1)
    assert n1.equals(n2)
    assert n2.equals(n1)
    assert n1 is not None
    assert not n1.equals(n3)
    assert not n3.equals(n1)


def test_close_tostring() -> None:
    n1: OnCompleted[int] = OnCompleted()
    assert "OnCompleted" in str(n1)


class CheckOnCompletedObserver(ObserverBase[Any]):
    def __init__(self) -> None:
        super().__init__()

        self.completed = False

    def on_next(self, value: Any) -> None:
        raise NotImplementedError()

    def on_error(self, error: Exception) -> None:
        raise NotImplementedError()

    def on_completed(self) -> None:
        self.completed = True


def test_close_accept_observer() -> None:
    obs = CheckOnCompletedObserver()
    n1: OnCompleted[Any] = OnCompleted()
    n1.accept(obs)
    assert obs.completed


def test_close_accept_observer_with_result() -> None:
    n1: OnCompleted[Any] = OnCompleted()

    def on_next(x: Any) -> None:
        assert False

    def on_error(err: Exception) -> None:
        assert False

    def on_completed() -> str:
        return "OK"

    # Cast is safe: AcceptObserver intentionally returns values for testing
    res = cast(str, n1.accept(AcceptObserver(on_next, on_error, on_completed)))
    assert "OK" == res


def test_close_accept_action() -> None:
    obs = [False]
    n1: OnCompleted[Any] = OnCompleted()

    def on_next(x: Any) -> None:
        assert False

    def on_error(ex: Exception) -> None:
        assert False

    def on_completed() -> None:
        obs[0] = True

    n1.accept(on_next, on_error, on_completed)
    assert obs[0]


def test_close_accept_action_with_result() -> None:
    n1: OnCompleted[Any] = OnCompleted()

    def on_next(x: Any) -> None:
        assert False

    def on_error(ex: Exception) -> None:
        assert False

    def on_completed() -> str:
        return "OK"

    # Cast is safe: testing internal behavior where callbacks return values
    res = cast(str, n1.accept(cast(Any, on_next), on_error, cast(Any, on_completed)))
    assert "OK" == res


def test_to_observable_empty() -> None:
    from reactivex import Observable

    scheduler = TestScheduler()

    def create() -> Observable[Any]:
        # Cast is safe: to_observable() returns Observable via Observable(subscribe)
        return cast(Observable[Any], OnCompleted[Any]().to_observable(scheduler))

    res = scheduler.start(create)
    assert res.messages == [ReactiveTest.on_completed(200)]


def test_to_observable_return() -> None:
    from reactivex import Observable

    scheduler = TestScheduler()

    def create() -> Observable[int]:
        # Cast is safe: to_observable() returns Observable via Observable(subscribe)
        return cast(Observable[int], OnNext(42).to_observable(scheduler))

    res = scheduler.start(create)
    assert res.messages == [
        ReactiveTest.on_next(200, 42),
        ReactiveTest.on_completed(200),
    ]


def test_to_observable_on_error() -> None:
    from reactivex import Observable

    ex = Exception("ex")
    scheduler = TestScheduler()

    def create() -> Observable[Any]:
        # Cast is safe: to_observable() returns Observable via Observable(subscribe)
        return cast(Observable[Any], OnError[Any](ex).to_observable(scheduler))

    res = scheduler.start(create)
    assert res.messages == [ReactiveTest.on_error(200, ex)]
