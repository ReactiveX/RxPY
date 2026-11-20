import pytest

import reactivex
from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.testing import TestScheduler


@pytest.mark.parametrize("kind", ["time", "duration_next", "duration_completed"])
def test_debounce_keeps_value_emitted_reentrantly(kind: str) -> None:
    scheduler = TestScheduler()
    source: Subject[int] = Subject()
    durations: list[Subject[None]] = [Subject(), Subject()]
    received: list[tuple[int, int]] = []
    completed: list[bool] = []

    def duration_mapper(value: int) -> reactivex.Observable[None]:
        return durations[value - 1]

    operator = (
        ops.debounce(10, scheduler=scheduler)
        if kind == "time"
        else ops.throttle_with_mapper(duration_mapper)
    )

    def on_next(value: int) -> None:
        received.append((scheduler.clock, value))
        if value == 1:
            source.on_next(2)

    source.pipe(operator).subscribe(
        on_next, on_completed=lambda: completed.append(True)
    )
    source.on_next(1)
    if kind == "time":
        scheduler.advance_to(10)
        scheduler.advance_to(20)
        expected = [(10, 1), (20, 2)]
    else:
        if kind == "duration_next":
            durations[0].on_next(None)
            durations[1].on_next(None)
        else:
            durations[0].on_completed()
            durations[1].on_completed()
        expected = [(0, 1), (0, 2)]
    source.on_completed()
    assert received == expected
    assert completed == [True]


@pytest.mark.parametrize("kind", ["time", "duration_next", "duration_completed"])
def test_debounce_reentrant_completion_does_not_repeat_emitted_value(kind: str) -> None:
    scheduler = TestScheduler()
    source: Subject[int] = Subject()
    duration: Subject[None] = Subject()
    received: list[int] = []
    completed: list[bool] = []
    operator = (
        ops.debounce(10, scheduler=scheduler)
        if kind == "time"
        else ops.throttle_with_mapper(lambda _: duration)
    )

    def on_next(value: int) -> None:
        received.append(value)
        source.on_completed()

    source.pipe(operator).subscribe(
        on_next, on_completed=lambda: completed.append(True)
    )
    source.on_next(1)
    if kind == "time":
        scheduler.advance_to(10)
    elif kind == "duration_next":
        duration.on_next(None)
    else:
        duration.on_completed()
    assert received == [1]
    assert completed == [True]


def test_throttle_synchronous_duration_reentrant_value() -> None:
    source: Subject[int] = Subject()
    received: list[int] = []

    def on_next(value: int) -> None:
        received.append(value)
        if value == 1:
            source.on_next(2)

    source.pipe(ops.throttle_with_mapper(lambda _: reactivex.empty())).subscribe(
        on_next
    )
    source.on_next(1)
    source.on_completed()
    assert received == [1, 2]
