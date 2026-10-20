import pytest

import reactivex
from reactivex import operators as ops
from reactivex.subject import Subject


@pytest.mark.parametrize("values", [[10, 20], (10, 20), range(10, 30, 10)])
def test_zip_iterable_repeated_subscriptions(values):
    zipped = reactivex.of(1, 2).pipe(ops.zip_with_iterable(values))
    first, second = [], []
    zipped.subscribe(first.append)
    zipped.subscribe(second.append)
    assert first == second == [(1, 10), (2, 20)]


def test_zip_iterable_overlapping_subscriptions():
    source = Subject()
    zipped = source.pipe(ops.zip_with_iterable([10, 20]))
    first, second = [], []
    a = zipped.subscribe(first.append)
    source.on_next(1)
    b = zipped.subscribe(second.append)
    source.on_next(2)
    a.dispose()
    source.on_next(3)
    b.dispose()
    assert first == [(1, 10), (2, 20)]
    assert second == [(2, 10), (3, 20)]


def test_zip_iterable_repeat():
    values = []
    reactivex.of(1, 2).pipe(ops.zip_with_iterable([10, 20]), ops.repeat(2)).subscribe(
        values.append
    )
    assert values == [(1, 10), (2, 20)] * 2


def test_zip_iterable_evaluates_iterable_lazily_per_subscription():
    iterations = []

    class Values:
        def __iter__(self):
            iterations.append(True)
            return iter([10])

    zipped = reactivex.just(1).pipe(ops.zip_with_iterable(Values()))
    assert iterations == []
    zipped.subscribe()
    zipped.subscribe()
    assert iterations == [True, True]


def test_zip_iterable_preserves_one_shot_iterator_behavior():
    zipped = reactivex.just(1).pipe(ops.zip_with_iterable(iter([10, 20])))
    values = []
    zipped.subscribe(values.append)
    zipped.subscribe(values.append)
    assert values == [(1, 10), (1, 20)]


def test_zip_iterable_failed_iteration_is_reported_to_subscriber():
    error = ValueError("cannot iterate")

    class Values:
        def __iter__(self):
            raise error

    zipped = reactivex.just(1).pipe(ops.zip_with_iterable(Values()))
    errors = []
    zipped.subscribe(on_error=errors.append)
    assert errors == [error]
