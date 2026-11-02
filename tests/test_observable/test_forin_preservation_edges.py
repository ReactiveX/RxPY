"""AI-assisted preservation controls for for_in's iterable semantics."""

import pytest

import reactivex
from reactivex.testing import ReactiveTest, TestScheduler


@pytest.mark.parametrize("values", [(), ((),), ((), ("α",), (), ("β", "γ"))])
def test_for_in_nested_empty_and_nonempty_sequences(
    values: tuple[tuple[str, ...], ...],
) -> None:
    mapped: list[tuple[str, ...]] = []
    received: list[str] = []
    completed: list[bool] = []

    def mapper(value: tuple[str, ...]) -> reactivex.Observable[str]:
        mapped.append(value)
        return reactivex.for_in(value, lambda item: reactivex.just(item))

    source = reactivex.for_in(values, mapper)
    assert mapped == []
    source.subscribe(received.append, on_completed=lambda: completed.append(True))

    assert mapped == list(values)
    assert received == [item for group in values for item in group]
    assert completed == [True]


def test_for_in_maps_lazily_and_observes_appended_values() -> None:
    scheduler = TestScheduler()
    values = [1]
    mapped: list[tuple[float, int]] = []

    def mapper(value: int) -> reactivex.Observable[int]:
        mapped.append((scheduler.clock, value))
        if value == 1:
            values.append(2)
        return scheduler.create_cold_observable(
            ReactiveTest.on_next(10, value), ReactiveTest.on_completed(20)
        )

    source = reactivex.for_in(values, mapper)
    assert mapped == []
    result = scheduler.start(lambda: source)

    assert mapped == [(200, 1), (220, 2)]
    assert values == [1, 2]
    assert result.messages == [
        ReactiveTest.on_next(210, 1),
        ReactiveTest.on_next(230, 2),
        ReactiveTest.on_completed(240),
    ]


def test_for_in_one_shot_iterator_resumes_after_disposal() -> None:
    scheduler = TestScheduler()
    values = iter([1, 2, 3])
    mapped: list[tuple[float, int]] = []

    def mapper(value: int) -> reactivex.Observable[int]:
        mapped.append((scheduler.clock, value))
        return scheduler.create_cold_observable(
            ReactiveTest.on_next(10, value), ReactiveTest.on_completed(20)
        )

    source = reactivex.for_in(values, mapper)
    first = scheduler.create_observer()
    subscription = source.subscribe(first, scheduler=scheduler)
    scheduler.advance_to(15)
    subscription.dispose()

    second = scheduler.create_observer()
    source.subscribe(second, scheduler=scheduler)
    scheduler.advance_to(60)

    assert mapped == [(0, 1), (15, 2), (35, 3)]
    assert first.messages == [ReactiveTest.on_next(10, 1)]
    assert second.messages == [
        ReactiveTest.on_next(25, 2),
        ReactiveTest.on_next(45, 3),
        ReactiveTest.on_completed(55),
    ]
    assert list(values) == []
