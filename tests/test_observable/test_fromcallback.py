import unittest
from typing import NoReturn

import reactivex
from reactivex.testing import ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex: Exception) -> NoReturn:
    raise RxException(ex)


class TestFromCallback(unittest.TestCase):
    def test_from_callback(self):
        res = reactivex.from_callback(lambda cb: cb(True))()

        def on_next(r):
            self.assertEqual(r, True)

        def on_error(err):
            assert False

        def on_completed():
            assert True

        res.subscribe(on_next, on_error, on_completed)

    def test_from_callback_single(self):
        res = reactivex.from_callback(lambda file, cb: cb(file))("file.txt")

        def on_next(r):
            self.assertEqual(r, "file.txt")

        def on_error(err):
            assert False

        def on_completed():
            assert True

        res.subscribe(on_next, on_error, on_completed)

    def test_from_node_callback_mapper(self):
        res = reactivex.from_callback(lambda f, s, t, cb: cb(f, s, t), lambda r: r[0])(
            1, 2, 3
        )

        def on_next(r):
            self.assertEqual(r, 1)

        def on_error(err):
            assert False

        def on_completed():
            assert True

        res.subscribe(on_next, on_error, on_completed)


def test_from_callback_repeated_subscriptions() -> None:
    calls = []

    def invoke(value, callback):
        calls.append(value)
        callback(value)

    source = reactivex.from_callback(invoke)(42)
    for _ in range(2):
        values = []
        completed = []
        source.subscribe(values.append, on_completed=lambda: completed.append(True))
        assert values == [42]
        assert completed == [True]
    assert calls == [42, 42]


def test_from_callback_overlapping_subscriptions() -> None:
    callbacks = []

    def invoke(value, callback):
        callbacks.append(callback)

    source = reactivex.from_callback(invoke)(42)
    first = []
    second = []
    source.subscribe(first.append)
    source.subscribe(second.append)
    callbacks[1](2)
    callbacks[0](1)
    assert first == [1]
    assert second == [2]


def test_from_callback_disposed_subscription_does_not_affect_next() -> None:
    callbacks = []

    def invoke(callback):
        callbacks.append(callback)

    source = reactivex.from_callback(invoke)()
    first = []
    second = []
    subscription = source.subscribe(first.append)
    subscription.dispose()
    source.subscribe(second.append)
    callbacks[0](1)
    callbacks[1](2)
    assert first == []
    assert second == [2]


def test_from_callback_mapper_completes_after_one_result() -> None:
    callbacks = []
    values = []
    completed = []

    def invoke(callback):
        callbacks.append(callback)

    source = reactivex.from_callback(invoke, lambda args: sum(args))()
    source.subscribe(values.append, on_completed=lambda: completed.append(True))
    callbacks[0](1, 2)
    callbacks[0](3, 4)
    assert values == [3]
    assert completed == [True]


def test_from_callback_mapper_repeat() -> None:
    from reactivex import operators as ops

    values = []
    completed = []
    reactivex.from_callback(lambda callback: callback(2), lambda args: args[0])().pipe(
        ops.repeat(2)
    ).subscribe(values.append, on_completed=lambda: completed.append(True))
    assert values == [2, 2]
    assert completed == [True]


def test_from_callback_mapper_failure() -> None:
    error = RuntimeError("mapper failed")
    values = []
    errors = []
    completed = []

    def mapper(args):
        raise error

    reactivex.from_callback(lambda callback: callback(1), mapper)().subscribe(
        values.append, errors.append, lambda: completed.append(True)
    )
    assert values == []
    assert errors == [error]
    assert completed == []


def test_from_callback_async_observer_error_propagates() -> None:
    import pytest

    callbacks = []
    errors = []
    error = RuntimeError("observer failed")

    def invoke(callback):
        callbacks.append(callback)

    def on_next(value):
        raise error

    reactivex.from_callback(invoke, lambda args: args[0])().subscribe(
        on_next, errors.append
    )
    with pytest.raises(RuntimeError) as raised:
        callbacks[0](1)
    assert raised.value is error
    assert errors == []
