import pytest

import reactivex
from reactivex import Observable
from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler


@pytest.mark.parametrize("syntax", ["pipe", "fluent", "subscript"])
@pytest.mark.parametrize(
    "start, stop, step",
    [
        (-5, 8, None),
        (-5, 3, None),
        (-20, 3, None),
        (-5, 20, None),
        (-1, 9, None),
        (-5, 8, 2),
        (-5, 0, None),
        (-5, None, 2),
        (-5, -1, 2),
    ],
)
def test_slice_matches_list_bounds(
    syntax: str, start: int, stop: int | None, step: int | None
) -> None:
    values = list(range(10))
    source = reactivex.from_iterable(values)
    if syntax == "pipe":
        result = source.pipe(ops.slice(start, stop, step))
    elif syntax == "fluent":
        result = source.slice(start, stop, step)
    else:
        result = source[start:stop:step]
    actual = []
    completed = []
    result.subscribe(actual.append, on_completed=lambda: completed.append(True))
    assert actual == values[start:stop:step]
    assert completed == [True]


def test_slice_mixed_bounds_waits_for_source_end() -> None:
    scheduler = TestScheduler()
    source = scheduler.create_hot_observable(
        *(ReactiveTest.on_next(210 + 10 * i, i) for i in range(10)),
        ReactiveTest.on_completed(320),
    )
    results = scheduler.start(lambda: source[-5:8])
    assert results.messages == [
        ReactiveTest.on_next(320, 5),
        ReactiveTest.on_next(320, 6),
        ReactiveTest.on_next(320, 7),
        ReactiveTest.on_completed(320),
    ]
    assert source.subscriptions == [ReactiveTest.subscribe(200, 320)]


def test_slice_mixed_bounds_does_not_complete_without_source_end() -> None:
    scheduler = TestScheduler()
    source = scheduler.create_hot_observable(
        *(ReactiveTest.on_next(210 + 10 * i, i) for i in range(10))
    )
    results = scheduler.start(lambda: source[-5:8])
    assert results.messages == []
    assert source.subscriptions == [ReactiveTest.subscribe(200, 1000)]


def test_slice_mixed_bounds_forwards_error_after_stop_index() -> None:
    scheduler = TestScheduler()
    error = RuntimeError("source failed")
    source = scheduler.create_cold_observable(
        *(ReactiveTest.on_next(10 + 10 * i, i) for i in range(10)),
        ReactiveTest.on_error(120, error),
    )
    results = scheduler.start(lambda: source[-5:8])
    assert results.messages == [ReactiveTest.on_error(320, error)]
    assert source.subscriptions == [ReactiveTest.subscribe(200, 320)]


def test_slice_mixed_bounds_resets_indices_on_repeat() -> None:
    values = []
    reactivex.from_iterable(range(10))[-5:8].pipe(ops.repeat(2)).subscribe(
        values.append
    )
    assert values == [5, 6, 7, 5, 6, 7]


def test_slice_mixed_bounds_overlapping_subscriptions() -> None:
    scheduler = TestScheduler()
    source = scheduler.create_cold_observable(
        *(ReactiveTest.on_next(10 + 10 * i, i) for i in range(10)),
        ReactiveTest.on_completed(120),
    )
    sliced = source[-5:8]
    first = scheduler.create_observer()
    second = scheduler.create_observer()
    sliced.subscribe(first, scheduler=scheduler)
    scheduler.schedule_relative(
        10, lambda *_: sliced.subscribe(second, scheduler=scheduler)
    )
    scheduler.start()
    assert first.messages == [
        ReactiveTest.on_next(120, 5),
        ReactiveTest.on_next(120, 6),
        ReactiveTest.on_next(120, 7),
        ReactiveTest.on_completed(120),
    ]
    assert second.messages == [
        ReactiveTest.on_next(130, 5),
        ReactiveTest.on_next(130, 6),
        ReactiveTest.on_next(130, 7),
        ReactiveTest.on_completed(130),
    ]


def test_slice_mixed_bounds_preserves_none_values() -> None:
    values = []
    reactivex.from_iterable([0, 1, None, 3, 4])[-3:4].subscribe(values.append)
    assert values == [None, 3]


def test_slice_mixed_bounds_rejects_negative_step() -> None:
    with pytest.raises(TypeError, match="Negative step not supported"):
        reactivex.from_iterable(range(10))[-5:8:-1]


def test_slice_mixed_bounds_empty_source() -> None:
    values = []
    completed = []
    source: Observable[int] = reactivex.empty()
    source[-5:8].subscribe(values.append, on_completed=lambda: completed.append(True))
    assert values == []
    assert completed == [True]
